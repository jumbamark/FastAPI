from .routers import post, user, auth, like
from .database import engine
from . import models
from fastapi import Depends, FastAPI, HTTPException, status, Response
from .config import settings


from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "https://www.google.com",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(like.router)


# path operation/ route
@app.get('/')
def root():
    return {"message": "Welcome to my API"}
