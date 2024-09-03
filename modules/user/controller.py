
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session, outerjoin, joinedload
from sqlalchemy.testing.pickleable import Order
from entities import *
from database import get_db
from helper.model import ResponseModel
from helper.status import StatusEnum
import datetime, random, string
from helper.authorization import is_user
from helper.supabase import SupabaseService
from modules.authentication.repositry import get_current_user, create_user, send_verification_email
from modules.user.model import * 

router = APIRouter(
    tags=["User"],
    prefix="/user"
)

@router.post("/create_user", operation_id="create_new_user", response_model=ResponseModel,
             description="Create new user")
def create_new_user(user_data: UserAccountCreate, db: Session = Depends(get_db)):
    existing_user = db.query(AccountDB).filter(AccountDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    verification_code = ''.join(random.choices(string.digits, k=6))

    new_user = create_user(db=db, username=user_data.username, email=user_data.email, password=user_data.password,
                           phone_number=user_data.phone_number, role_id=1)
    new_user.verification_code = verification_code
    db.commit()

    send_verification_email(user_data.email, verification_code)

    return ResponseModel(code=status.HTTP_200_OK,
                         status=StatusEnum.Success.value,
                         message="User created successfully. Please check your email for verification code.")