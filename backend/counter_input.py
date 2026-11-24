from datetime import date
from pydantic import BaseModel, Field

class Receipt(BaseModel):
    voucher: str = Field(pattern=r"^[A-Z0-9-]{4,18}$")
    counter: str = Field(pattern=r"^[A-Z0-9-]{2,12}$")
    used_on: date
    receipt: str = Field(pattern=r"^[A-Z0-9-]{4,24}$")
