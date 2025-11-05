from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):

    password: str = Field(
        ...,
        min_length=12,
        max_length=256,
        title="Password",
        description="User password must be between 12 and 256 characters"
    )

class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
