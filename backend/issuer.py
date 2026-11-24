from voucher_dates import each_month
from month_guard import lock_ledger, verify_open

def issue(cx, voucher):
    lock_ledger(cx)
    for month in each_month(voucher.issued_on,voucher.expires_on):
        verify_open(cx,month)
    return cx.execute("""
      INSERT INTO meal_vouchers(code,batch,issued_on,expires_on)
      VALUES (%s,%s,%s,%s) RETURNING *
    """,(voucher.code,voucher.batch,voucher.issued_on,voucher.expires_on)).fetchone()

def inventory(cx):
    return cx.execute("""
      SELECT v.*,b.counter,c.name AS counter_name, r.receipt IS NOT NULL AS redeemed
      FROM meal_vouchers v JOIN meal_batches b ON b.code=v.batch
      JOIN meal_counters c ON c.code=b.counter
      LEFT JOIN meal_redemptions r ON r.voucher=v.code AND NOT EXISTS (
        SELECT 1 FROM meal_reversals x WHERE x.redemption_id=r.id)
      ORDER BY v.code LIMIT 300
    """).fetchall()
