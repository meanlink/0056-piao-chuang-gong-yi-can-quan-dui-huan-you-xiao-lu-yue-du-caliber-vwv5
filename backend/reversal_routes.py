from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, StringConstraints
from core import db, require
from reversal_policy import reverse

router = APIRouter(prefix="/counter")

class Correction(BaseModel):
    reason: Annotated[str, StringConstraints(strip_whitespace=True,min_length=4,max_length=120)]

@router.post("/receipts/{id}/reversal",status_code=201)
def correct(id:int,body:Correction,user=Depends(require("reviewer"))):
    with db() as cx:
        return reverse(cx,id,body.reason,user["email"])
