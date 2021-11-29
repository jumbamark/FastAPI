from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from pydantic.networks import EmailStr
from typing import Optional

from pydantic.types import conint


# what we want the user to pass in
# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True


# User schema
# requests
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# response
class UserOut(BaseModel):
    id: int
    email: EmailStr
    time_created: datetime

    class Config:
        orm_mode = True


# Post schema
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# Requests
class PostCreate(PostBase):
    pass   # by default automatically inherits all the fields in PostBase.


class PostUpdate(PostBase):
    title: str
    content: str
    published: bool


# Response - return posts
class Post(PostBase):
    id: int
    time_posted: datetime
    # owner_id: int
    owner: UserOut
    # we are not sending back the owner_id

    class Config:
        orm_mode = True


# Response - return results
class PostResults(BaseModel):
    Post: Post
    total_likes: int

    class Config:
        orm_mode = True


# Auth schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for access token and token type
class Token(BaseModel):
    access_token: str
    token_type: str


# schema for the token data (data embedded into our access_token)
class TokenData(BaseModel):
    id: Optional[str] = None


# Schema for our voting
class Like(BaseModel):
    post_id: int
    dir: conint(le=1)
