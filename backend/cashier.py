from fastapi import HTTPException
from month_guard import lock_ledger, verify_open
from voucher_dates import month_start

def redeem(cx, data):
    lock_ledger(cx)
    verify_open(cx,month_start(data.used_on))
    voucher = cx.execute("""
      SELECT v.*,b.counter FROM meal_vouchers v JOIN meal_batches b ON v.batch=b.code WHERE v.code=%s
    """,(data.voucher,)).fetchone()
    if not voucher:
        raise HTTPException(404,"没有这个券码")
    if not voucher["issued_on"] <= data.used_on <= voucher["expires_on"]:
        raise HTTPException(409,"核销日期超出券有效期")
    if voucher["counter"] != data.counter:
        raise HTTPException(409,"该批次只能由指定的餐站核销")
    old = cx.execute("""
      SELECT 1 FROM meal_redemptions r WHERE voucher=%s
      AND NOT EXISTS (SELECT 1 FROM meal_reversals a WHERE a.redemption_id=r.id)
    """,(data.voucher,)).fetchone()
    if old:
        raise HTTPException(409,"该券已有一笔未冲回的核销")
    return cx.execute("INSERT INTO meal_redemptions(voucher,counter,used_on,receipt) VALUES (%s,%s,%s,%s) RETURNING *",
                      (data.voucher,data.counter,data.used_on,data.receipt)).fetchone()
