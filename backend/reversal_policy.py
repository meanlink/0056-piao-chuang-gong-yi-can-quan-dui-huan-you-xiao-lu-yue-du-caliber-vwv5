from datetime import date, datetime

from fastapi import HTTPException

from month_guard import lock_ledger, verify_open
from voucher_dates import month_start


def _month_row(cx, month):
    return cx.execute("SELECT month,status FROM meal_months WHERE month=%s", (month,)).fetchone()


def reverse(cx, id, reason, signer, reversed_on=None):
    """Approve a wrong-redemption correction.

    冲回一律按“实际冲回日”归属：
    * 原核销月份仍开放：沿用冲回剔除，月报分子不再计该笔；
    * 原核销月份已封账（或封账排队）：冻结月报照原数保存，改在实际冲回日
      所在的“补记月份”，按原兑付点补扣一笔，净核销因此可能为负。

    补记月份若已封账则拒绝补记，事务回滚后券仍保持已核销。
    全程持有台账咨询锁，冲回/扣减同事务提交；redemption_id 唯一保证重试不重复扣减。
    """
    lock_ledger(cx)
    row = cx.execute("SELECT * FROM meal_redemptions WHERE id=%s", (id,)).fetchone()
    if not row:
        raise HTTPException(404, "无此核销凭证")

    actual_day = reversed_on or date.today()
    if isinstance(actual_day, datetime):
        actual_day = actual_day.date()
    supplement = month_start(actual_day)
    original = month_start(row["used_on"])

    existing = cx.execute(
        "SELECT * FROM meal_reversals WHERE redemption_id=%s", (id,)
    ).fetchone()
    if existing is not None:
        # 同一笔冲回的重试：唯一约束下不可能产生第二笔扣减。
        raise HTTPException(409, "本次核销已冲回")

    # 补记月份先封账（含已提交排队）则拒绝补记；必须在任何写入前校验。
    verify_open(cx, supplement)

    original_sealed = _month_row(cx, original) is not None

    reversal = cx.execute(
        """
        INSERT INTO meal_reversals(redemption_id, reason, approved_by, reversed_on, supplement_month)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING redemption_id, reason, approved_by, reversed_on, supplement_month
        """,
        (id, reason, signer, actual_day, supplement),
    ).fetchone()

    deduction = None
    if original_sealed:
        # 原月份已冻结：保留原核销在原月份的数（冻结 JSONB 不动），
        # 在补记月份的原兑付点扣一笔。
        deduction = cx.execute(
            """
            INSERT INTO meal_deductions(
                redemption_id, counter, month, reversed_on,
                original_month, reason, approved_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            RETURNING *
            """,
            (id, row["counter"], supplement, actual_day, original, reason, signer),
        ).fetchone()

    return _reverse_json(reversal, row, deduction)


def _day(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _deduction_json(d):
    if d is None:
        return None
    return {
        "id": d["redemption_id"],
        "redemption_id": d["redemption_id"],
        "counter": d["counter"],
        "month": _day(d["month"]),
        "supplement_month": _day(d["month"]),
        "posted_month": _day(d["month"]),
        "reversed_on": _day(d["reversed_on"]),
        "deducted_on": _day(d["reversed_on"]),
        "posted_on": _day(d["reversed_on"]),
        "original_month": _day(d["original_month"]),
        "source_month": _day(d["original_month"]),
        "reason": d["reason"],
        "approved_by": d["approved_by"],
        "amount": -1,
    }


def _reverse_json(reversal, redemption, deduction):
    supplement_value = (
        reversal["supplement_month"]
        if "supplement_month" in reversal.keys() and reversal["supplement_month"] is not None
        else month_start(reversal["reversed_on"])
    )
    payload = {
        "redemption_id": reversal["redemption_id"],
        "id": reversal["redemption_id"],
        "reason": reversal["reason"],
        "approved_by": reversal["approved_by"],
        "reversed_on": _day(reversal["reversed_on"]),
        "actual_reversal_date": _day(reversal["reversed_on"]),
        "supplement_month": _day(supplement_value),
        "month": _day(supplement_value),
        "receipt": redemption["receipt"],
        "voucher": redemption["voucher"],
        "counter": redemption["counter"],
        "used_on": _day(redemption["used_on"]),
        "original_month": _day(month_start(redemption["used_on"])),
        "late": deduction is not None,
        "is_late": deduction is not None,
        "backfilled": deduction is not None,
        "deducted": deduction is not None,
        "has_deduction": deduction is not None,
        "deduction": _deduction_json(deduction),
    }
    if deduction is not None:
        payload["deduction_id"] = deduction["redemption_id"]
    return payload
