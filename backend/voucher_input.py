from datetime import date
from pydantic import BaseModel, Field, model_validator

class Voucher(BaseModel):
    code: str = Field(pattern=r"^[A-Z0-9-]{4,18}$")
    batch: str = Field(pattern=r"^[A-Z0-9-]{4,18}$")
    issued_on: date
    expires_on: date

    @model_validator(mode="after")
    def valid_window(self):
        if not 0 <= (self.expires_on-self.issued_on).days <= 180:
            raise ValueError("发券窗应为 1 至 181 天")
        return self
