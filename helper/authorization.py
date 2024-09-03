from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from entities import AccountDB

def is_user(current_user: dict, db: Session):
    user = db.query(AccountDB).filter(AccountDB.id == current_user['id']).first()
    if user.role_id != 1:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Forbidden",
    )

def is_staff(current_user: dict, db: Session):
    user = db.query(AccountDB).filter(AccountDB.id == current_user['id']).first()
    if user.role_id != 2:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Forbidden",
    )


def is_admin(current_user: dict, db: Session):
    user = db.query(AccountDB).filter(AccountDB.id == current_user['id']).first()
    if user.role_id != 3:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Forbidden",
    )
