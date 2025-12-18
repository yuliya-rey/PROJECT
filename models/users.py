from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "email": "user@example.com",
                "username": "ivanov"
            }]
        }
    }

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
