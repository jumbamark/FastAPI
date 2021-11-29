from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange


app = FastAPI()


# path operation/ route
@app.get('/')
def root():
    return {"message": "Welcome to my API"}


# saving our fields in memory
my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favourite foods", "content": "I like salads", "id": 2}
]


# Retrieving a bunch of social media posts from our application
@app.get('/posts')
def get_posts():
    return {"data": my_posts}


# creating a post request
@app.post('/createposts')
# Body extracts all of the fields from the body, converts it into python dict and stores it into a variable named payload.
def create_posts(payload: dict = Body(...)):
    print(payload)
    # return {"Message": "You've succesfully created a post"}
    return {"new_post": f"title:{payload['title']}  content:{payload['content']}"}


# Using a schema - automatically performs validations
# title- str, content- str (what we want the user to pass in)
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    print(post.rating)
    print(post.dict())  # converts into a dict
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 100000)
    my_posts.append(post_dict)
    return {"data": post_dict}


# latest post - ORDER matters(works top down)
@app.get('/posts/latest')
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"detail": post}


def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post


# Retrieving one individual post - id field reps a path parameter
@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    print(type(id))
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

        # response.status_code = 404
        # response.status_code = status.HTTP_404_NOT_FOUND
        # is going to ever run if post doesn't exist'
        # return {"message": f"post with id: {id} was not found"}

    return {"post_detail": post}


def find_index_post(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index


# deleting a post
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # find the index in the array that has required ID
    # my_posts.pop(index)
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    my_posts.pop(index)
    # return {"message": "post was succesfully deleted"}
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict

    return {"data": post_dict}
