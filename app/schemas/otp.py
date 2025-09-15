from pydantic import BaseModel

class OTPBase(BaseModel):
    user_id: int

class OTPCreate(OTPBase):
    secret: str

class OTPRead(OTPBase):
    id: int
    secret: str

    class Config:
        from_attributes = True
