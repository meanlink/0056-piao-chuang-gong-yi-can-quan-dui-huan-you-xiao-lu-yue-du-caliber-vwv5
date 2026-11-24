from fastapi import APIRouter, Depends, HTTPException

from core import db, require
from exposure import deduction_details
from month_close import preview, submit
from voucher_dates import parse_month

router = APIRouter(prefix="/voucher-months")


def _month(value: str):
    try:
        return parse_month(value)
    except (ValueError, TypeError):
        raise HTTPException(422, "月份格式应为 YYYY-MM-DD 或 YYYY-MM")


@router.get("")
@router.get("/")
def list_months(_=Depends(require())):
    with db() as cx:
        rows = cx.execute(
            """
            SELECT m.month,m.status,m.approved_by,m.job_id,m.result,
                   j.status AS job_status
            FROM meal_months m LEFT JOIN app_jobs j ON j.id=m.job_id
            ORDER BY m.month DESC
            """
        ).fetchall()
        for r in rows:
            if hasattr(r["month"], "isoformat"):
                r["month"] = r["month"].isoformat()
        return {"months": rows, "items": rows}


@router.get("/{month}")
def report(month: str, _=Depends(require())):
    with db() as cx:
        return preview(cx, _month(month))


@router.get("/{month}/deductions")
def month_deductions(month: str, _=Depends(require())):
    m = _month(month)
    with db() as cx:
        details = deduction_details(cx, m)
        return {"month": m.isoformat(), "deductions": details, "items": details}


@router.post("/{month}/close", status_code=202)
def close(month: str, user=Depends(require("reviewer"))):
    with db() as cx:
        return submit(cx, _month(month), user["email"])
