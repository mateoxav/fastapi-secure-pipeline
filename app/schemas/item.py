from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ItemRead(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

