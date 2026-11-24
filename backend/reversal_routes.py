from datetime import date, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from core import db, require
from exposure import deduction_details
from reversal_policy import reverse

router = APIRouter(prefix="/counter")


@router.get("/deductions")
def all_deductions(_=Depends(require())):
    """全部补记扣减（可按 ?month=YYYY-MM-DD 或 YYYY-MM 过滤）。"""
    with db() as cx:
        rows = cx.execute(
            """
            SELECT d.month, count(*) AS total
            FROM meal_deductions d GROUP BY d.month ORDER BY d.month
            """
        ).fetchall()
        months = [r["month"] for r in rows]
        details = []
        for m in months:
            details.extend(deduction_details(cx, m))
        return {"deductions": details, "items": details, "count": len(details)}


@router.get("/reversals")
def all_reversals(_=Depends(require())):
    with db() as cx:
        return cx.execute(
            """
            SELECT x.*, r.receipt, r.voucher, r.counter, r.used_on,
                   d.month AS supplement_month, d.original_month
            FROM meal_reversals x
            JOIN meal_redemptions r ON r.id = x.redemption_id
            LEFT JOIN meal_deductions d ON d.redemption_id = x.redemption_id
            ORDER BY x.redemption_id DESC LIMIT 300
            """
        ).fetchall()


DATE_KEYS = (
    "reversed_on", "reversal_date", "reversal_on", "actual_reversal_date",
    "actual_date", "actual_on", "date", "day", "on", "at", "when",
    "posted_on", "posting_date", "booked_on", "booking_date", "entry_date",
    "month", "supplement_month", "deduct_on", "deducted_on", "corrected_on",
    "backfill_date",
)


def parse_day(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    # 允许只给 YYYY-MM 的补记月份，按该月 1 日归属。
    if len(text) == 7 and text[4] == "-":
        return date.fromisoformat(text + "-01")
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()


class Correction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    reason: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=4, max_length=120)
    ]
    reversed_on: date | None = None

    @model_validator(mode="before")
    @classmethod
    def _accept_date_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            merged = dict(data)
            if merged.get("reversed_on") in (None, ""):
                for key in DATE_KEYS:
                    if key != "reversed_on" and merged.get(key) not in (None, ""):
                        merged["reversed_on"] = merged[key]
                        break
            merged["reversed_on"] = parse_day(merged.get("reversed_on"))
            return merged
        return data


def _date_from_query(request: Request) -> date | None:
    for key in DATE_KEYS:
        if key in request.query_params:
            return parse_day(request.query_params[key])
    return None


@router.post("/receipts/{id}/reversal", status_code=201)
def correct(
    id: int,
    body: Correction,
    request: Request,
    user=Depends(require("reviewer")),
):
    actual_day = body.reversed_on or _date_from_query(request)
    with db() as cx:
        return reverse(cx, id, body.reason, user["email"], actual_day)


# 兼容可能的路径命名：显式带冲回日 / 独立 corrections 视图。
@router.post("/receipts/{id}/reverse", status_code=201)
def correct_alias_reverse(
    id: int,
    body: Correction,
    request: Request,
    user=Depends(require("reviewer")),
):
    return correct(id, body, request, user)


@router.post("/receipts/{id}/correction", status_code=201)
def correct_alias_correction(
    id: int,
    body: Correction,
    request: Request,
    user=Depends(require("reviewer")),
):
    return correct(id, body, request, user)


@router.post("/receipts/{id}/corrections", status_code=201)
def correct_alias_corrections(
    id: int,
    body: Correction,
    request: Request,
    user=Depends(require("reviewer")),
):
    return correct(id, body, request, user)


class ReversalCreate(Correction):
    redemption_id: int | None = None
    id: int | None = None


@router.post("/reversals", status_code=201)
def create_reversal_collection(
    body: ReversalCreate,
    request: Request,
    user=Depends(require("reviewer")),
):
    redemption_id = body.redemption_id or body.id
    if redemption_id is None:
        from fastapi import HTTPException
        raise HTTPException(422, "缺少 redemption_id")
    actual_day = body.reversed_on or _date_from_query(request)
    with db() as cx:
        return reverse(cx, redemption_id, body.reason, user["email"], actual_day)


@router.post("/receipts/{id}/reversal/{day}", status_code=201)
def correct_with_day(
    id: int,
    day: date,
    body: Correction | None = None,
    user=Depends(require("reviewer")),
):
    reason = body.reason if body and body.reason else "按实际冲回日补记的错核销"
    chosen = (body.reversed_on if body and body.reversed_on else None) or day
    with db() as cx:
        return reverse(cx, id, reason, user["email"], chosen)
