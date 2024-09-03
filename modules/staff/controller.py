from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, Session
from database import get_db
from entities import ProductCategoryDB
from modules.staff.model import * 
from helper.model import ResponseModel
from helper.status import StatusEnum
from modules.authentication.controller import get_current_user

router = APIRouter(
    tags=["Staff"],
    prefix="/staff"
)

@router.get("/testing")
def testing():
    return "hello world"
