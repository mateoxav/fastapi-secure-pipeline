from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.core.security import decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Dependency to get the current authenticated user
    user_id = decode_token(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not user_id:
        raise credentials_exception
    user = db.get(User, int(user_id)) # Using modern Session.get()
    if not user or not user.is_active:
        raise credentials_exception
    return user

@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Create a new item for the current user.
    item = Item(**payload.model_dump(), owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/", response_model=List[ItemRead])
def get_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retrieve all items for the current user.
    return db.query(Item).filter(Item.owner_id == current_user.id).all()

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retrieve a specific item by its ID.
    item = db.get(Item, item_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Update an existing item.
    item = db.get(Item, item_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Delete an item. 
    item = db.get(Item, item_id)
    if item and item.owner_id == current_user.id:
        db.delete(item)
        db.commit()
    # Always return 204 to avoid leaking information about item existence
    return None