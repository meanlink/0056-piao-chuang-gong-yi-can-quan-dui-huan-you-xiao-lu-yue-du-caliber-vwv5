from fastapi import HTTPException
from month_guard import lock_ledger, verify_open
from voucher_dates import month_start

def reverse(cx,id,reason,signer):
    lock_ledger(cx)
    row = cx.execute("SELECT * FROM meal_redemptions WHERE id=%s",(id,)).fetchone()
    if not row:
        raise HTTPException(404,"无此核销凭证")
    verify_open(cx,month_start(row["used_on"]))
    result = cx.execute("""
      INSERT INTO meal_reversals VALUES (%s,%s,%s) ON CONFLICT DO NOTHING RETURNING *
    """,(id,reason,signer)).fetchone()
    if result is None:
        raise HTTPException(409,"本次核销已冲回")
    return result
