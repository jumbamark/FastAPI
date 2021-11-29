from fastapi import Depends, FastAPI, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from ORM.oauth2 import get_current_user

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/like",
    tags=["Likes"]
)


# posting likes
@router.post("/", status_code=status.HTTP_201_CREATED)
def like(like: schemas.Like, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # liking a post that doesn't exist
    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {like.post_id} does not exist")

    # if we want to create a vote the first thing is to query to see does the vote already exist
    # check to see if; there's already a vote for the specific post_id, the specific user has liked this post already
    # this(like_query) is not going to query the db yet it's just bulding up a query; it checks to see if the specific user ultimately has liked the specific post already
    like_query = db.query(models.Like).filter(
        models.Like.post_id == like.post_id, models.Like.user_id == current_user.id)
    already_liked = like_query.first()

    # logic for when the vote direction is 1
    if (like.dir == 1):
        if already_liked:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already liked post {like.post_id}")
        new_vote = models.Like(post_id=like.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully liked"}

    else:
        if not already_liked:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"You've not liked this post before")
        like_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "successfully unliked"}
