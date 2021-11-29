from fastapi import Depends, FastAPI, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy.sql.functions import func

from ORM.oauth2 import get_current_user

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


# Retrieving posts
# @router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostResults])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    print(search)

    # return all posts
    posts = db.query(models.Post).all()
    # adding limit parameter to our query
    posts = db.query(models.Post).limit(limit).all()
    # adding skip to our query
    posts = db.query(models.Post).limit(limit).offset(skip).all()
    # adding search to our query
    posts = (db.query(models.Post).filter(
        models.Post.content.contains(search)).limit(limit).offset(skip).all())

    # return posts for a specific user that's logged in
    # posts = db.query(models.Post).filter(
    #     models.Post.owner_id == current_user.id).all()

    # return posts

    # retrieving posts and total number of likes
    results = (db.query(models.Post,
                        func.count(
                            models.Like.post_id).label("total_likes")).join(
                                models.Like,
                                models.Like.post_id == models.Post.id,
                                isouter=True).group_by(models.Post.id))
    print(results)

    # perform the query
    results = (db.query(
        models.Post,
        func.count(models.Like.post_id).label("total_likes")).join(
            models.Like, models.Like.post_id == models.Post.id,
            isouter=True).group_by(models.Post.id).filter(
                models.Post.content.contains(search)).limit(limit).offset(
                    skip).all())

    return results


# Creating a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user)
    print(current_user.id)
    print(current_user.email)
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    print(post.dict())
    new_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Retrieving one individual post
# @router.get('/{id}', response_model=schemas.Post)
@router.get("/{id}", response_model=schemas.PostResults)
def get_post(
        id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    # If we did find a post; logic to make sure a user only gets their post
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f"Not authorized to perform requested action")

    # return post

    results = (db.query(
        models.Post,
        func.count(models.Like.post_id).label("total_likes")).join(
            models.Like, models.Like.post_id == models.Post.id,
            isouter=True).group_by(
                models.Post.id).filter(models.Post.id == id).first())

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )

    return results


# deleting a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
        id: int,
        db: Session = Depends(get_db),
        current_user: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    print(post_query)
    print(post)

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    # If we did find a post; logic to make sure a user only deletes their post
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int,
                updated_post: schemas.PostUpdate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist",
        )

    # If we did find a post; logic to make sure a user only updates their post
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to perform requested action",
        )

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
