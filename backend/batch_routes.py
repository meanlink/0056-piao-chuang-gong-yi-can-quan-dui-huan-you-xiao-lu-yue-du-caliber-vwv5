from fastapi import APIRouter, Depends
from core import db, require
from issuer import inventory, issue
from voucher_input import Voucher

router=APIRouter()

@router.get("/issuer")
def desk(_=Depends(require())):
    with db() as cx:
        return {"vouchers":inventory(cx),"batches":cx.execute("SELECT * FROM meal_batches ORDER BY code").fetchall(),
                "counters":cx.execute("SELECT * FROM meal_counters ORDER BY code").fetchall()}

@router.post("/issuer/vouchers",status_code=201)
def mint(body:Voucher,_=Depends(require("operator"))):
    with db() as cx:
        return issue(cx,body)
