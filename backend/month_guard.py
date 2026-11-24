from fastapi import HTTPException

def lock_ledger(cx):
    cx.execute("SELECT pg_advisory_xact_lock(163805)")

def verify_open(cx,month):
    exists = cx.execute("SELECT 1 FROM meal_months WHERE month=%s",(month,)).fetchone()
    if exists:
        raise HTTPException(409,"凭证影响已冻结月份，请联系月结复核员")
