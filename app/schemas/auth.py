from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    device_trusted: bool | None = None
    new_device: bool | None = None


class LoginStepUpResponse(BaseModel):
    step_up_required: bool = True
    device_id: int
    options: dict


class PasskeyLoginVerifyRequest(BaseModel):
    credential: dict