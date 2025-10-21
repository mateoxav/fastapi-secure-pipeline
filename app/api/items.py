from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import get_db
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.core.security import decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # Decode token and fetch user or fail
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user

@router.post("/", response_model=ItemRead, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Item(name=payload.name, description=payload.description, owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Item).get(item_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Item).get(item_id)
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.name is not None:
        item.name = payload.name
    if payload.description is not None:
        item.description = payload.description
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Item).get(item_id)
    if not item or item.owner_id != current_user.id:
        # Avoid leaking IDs; return 204 for idempotency could be another option
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None