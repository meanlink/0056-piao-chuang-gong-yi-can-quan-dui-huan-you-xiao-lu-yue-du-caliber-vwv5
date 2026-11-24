from datetime import date
from fastapi import APIRouter, Depends
from core import db, require
from month_close import preview,submit

router=APIRouter(prefix="/voucher-months")

@router.get("/{month}")
def report(month:date,_=Depends(require())):
    with db() as cx:
        return preview(cx,month)

@router.post("/{month}/close",status_code=202)
def close(month:date,user=Depends(require("reviewer"))):
    with db() as cx:
        return submit(cx,month,user["email"])
