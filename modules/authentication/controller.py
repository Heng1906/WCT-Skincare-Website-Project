from fastapi import Depends, HTTPException, status, APIRouter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Importing from local files
from database import get_db
from entities import AccountDB
from modules.user.model import AccountCreate
from modules.authentication.model import UserToken
from modules.authentication.repositry import *
from helper.authorization import is_user, is_staff
from helper.model import ResponseModel
from helper.status import StatusEnum

router = APIRouter(
    tags=["Auth"]
)

@router.post("/create_user")
def create_new_user(user_data: AccountCreate, db: Session = Depends(get_db)):
    existing_user = db.query(AccountDB).filter(AccountDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    verification_code = ''.join(random.choices(string.digits, k=6))
    
    new_user = create_user(db=db, username=user_data.username, email=user_data.email, password=user_data.password, phone_number=user_data.phone_number, role_id=user_data.role_id)
    new_user.verification_code = verification_code
    db.commit()
    
    send_verification_email(user_data.email, verification_code)
    return ResponseModel(
                code = status.HTTP_200_OK,
                status = StatusEnum.Success.value,
                message = "User created successfully. Please check your email for verification code."
            )

@router.post("/verify_code")
def verify_code_and_get_tokens(email: str, verification_code: str, db: Session = Depends(get_db)):
    user = db.query(AccountDB).filter(AccountDB.email == email, AccountDB.verification_code == verification_code).first()
    if user:
        user.verification_code = None
        db.commit()

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(data={"sub": user.email, "id": user.id, "type": "access_token"}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id, "type": "refresh_token"}, expires_delta=refresh_token_expires)
        return ResponseModel(
            code = status.HTTP_200_OK,
            status = StatusEnum.Success.value,
            result = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/sign_in")
def sign_in_for_access_token(form_data: UserToken, db: Session = Depends(get_db)):
    user = db.query(AccountDB).filter(AccountDB.email == form_data.email).first()
    if user and pwd_context.verify(form_data.password, user.password_hash):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        access_token = create_access_token(data={"sub": user.email, "id": user.id, "type": "access_token"}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id, "type": "refresh_token"}, expires_delta=refresh_token_expires)
        return ResponseModel(
            code = status.HTTP_200_OK,
            status = StatusEnum.Success.value,
            result = {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/refresh_token")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_refresh_token(refresh_token, credentials_exception)
    user = db.query(AccountDB).filter(AccountDB.email == payload.get("sub")).first()
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.email, "id": user.id, "type": "access_token"}, expires_delta=access_token_expires)
        return ResponseModel(
            code = status.HTTP_200_OK,
            status = StatusEnum.Success.value,
            result = {"access_token": access_token, "token_type": "bearer"}
        )
    
    raise credentials_exception

@router.post("/forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(AccountDB).filter(AccountDB.email == email).first()
    if user:
        reset_token = generate_reset_token()
        if save_reset_token(db, email, reset_token):
            send_password_reset_email(email, reset_token)
            return ResponseModel(
                code = status.HTTP_200_OK,
                status = StatusEnum.Success.value,
                message = "Password reset link sent to your email"
            )
    return ResponseModel(
                code = status.HTTP_200_OK,
                status = StatusEnum.Success.value,
                message = "If an account with this email exists, a password reset link has been sent to your email"
            )

@router.post("/reset_password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(AccountDB).filter(AccountDB.reset_token == token).first()
    if user:
        email = user.email
        if reset_password_func(db, email, token, new_password):
            return ResponseModel(
                code = status.HTTP_200_OK,
                status = StatusEnum.Success.value,
                message = "Password reset successfully"
            )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )

def reset_password_func(db: Session, email: str, token: str, new_password: str):
    user = db.query(AccountDB).filter(AccountDB.email == email).first()
    if user and user.reset_token == token and user.reset_token_expires > datetime.utcnow():
        user.password_hash = pwd_context.hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        return True
    return False

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    is_user(current_user, db)
    return ResponseModel(
            code = status.HTTP_200_OK,
            status = StatusEnum.Success.value,
            result = {"message": "This route is protected", "user": current_user["id"]}
        )
