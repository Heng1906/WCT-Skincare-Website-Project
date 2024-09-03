from typing import Optional
from fastapi import UploadFile, File
from pydantic import BaseModel


# Pydantic model for user creation
class AccountCreate(BaseModel):
    username: str
    email:str
    password: str
    phone_number: str
    role_id: str





