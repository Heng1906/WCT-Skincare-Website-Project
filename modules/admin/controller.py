from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import sessionmaker, Session
from database import get_db
from entities import ProductCategoryDB
from helper.model import ResponseModel
from helper.status import StatusEnum
from modules.authentication.controller import get_current_user

router = APIRouter(
    tags=["Admin"],
    prefix="/admin"
)

@router.get("/testing")
def testing():
    return "hello world"
