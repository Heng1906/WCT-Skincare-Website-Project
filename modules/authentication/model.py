from pydantic import BaseModel

class UserToken(BaseModel):
    email: str
    password: str
