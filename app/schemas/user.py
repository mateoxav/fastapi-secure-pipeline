from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):

    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        title="Password",
        description="User password must be between 8 and 72 characters"
    )

class UserRead(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
