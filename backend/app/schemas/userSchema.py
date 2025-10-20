from typing import Annotated

from pydantic import BaseModel, Field


class MessageResponseSchema(BaseModel):
    message: str


class UserCreateSchema(BaseModel):
    phoneNumber: Annotated[str, Field(..., example="+1234567890")]
    fullName: Annotated[str, Field(..., example="John Doe")]
    password: Annotated[str, Field(..., min_length=8, example="strongpassword123")]


class UserUpdateSchema(BaseModel):
    fullName: Annotated[str, Field(None, example="John Doe")]
    phoneNumber: Annotated[str, Field(None, example="+1234567890")]
    isVerified: Annotated[bool, Field(None, example=True)]


class UserResponseSchema(BaseModel):
    Id: int
    phoneNumber: str
    fullName: str
    isVerified: bool
    createdAt: str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    phoneNumber: Annotated[str, Field(..., example="+1234567890")]
    password: Annotated[str, Field(..., min_length=8, example="strongpassword123")]


class UserForgotPasswordSchema(BaseModel):
    phoneNumber: Annotated[str, Field(..., example="+1234567890")]


class UserChangePasswordSchema(BaseModel):
    oldPassword: Annotated[str, Field(..., min_length=8, example="oldpassword123")]
    newPassword: Annotated[
        str, Field(..., min_length=8, example="newstrongpassword456")
    ]


class UserResetPasswordSchema(BaseModel):
    phoneNumber: Annotated[str, Field(..., example="+1234567890")]
    newPassword: Annotated[
        str, Field(..., min_length=8, example="newstrongpassword456")
    ]


class VerifyOtpSchema(BaseModel):
    phoneNumber: Annotated[str, Field(..., example="+1234567890")]
    otpCode: Annotated[str, Field(..., min_length=6, max_length=6, example="123456")]
