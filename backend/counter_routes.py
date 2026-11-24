from fastapi import APIRouter, Depends
from core import db, require
from cashier import redeem
from counter_input import Receipt

router=APIRouter(prefix="/counter")

@router.get("/receipts")
def list_receipts(_=Depends(require())):
    with db() as cx:
        return cx.execute("""
          SELECT r.*,x.reason,x.approved_by FROM meal_redemptions r LEFT JOIN meal_reversals x ON x.redemption_id=r.id
          ORDER BY r.id DESC LIMIT 300
        """).fetchall()

@router.post("/receipts",status_code=201)
def collect(body:Receipt,_=Depends(require("operator"))):
    with db() as cx:
        return redeem(cx,body)
