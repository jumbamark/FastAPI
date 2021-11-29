from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
# gives the column names as well as the values - makes it a nice python dict
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()


# Using a schema - automatically performs validations
# title- str, content- str (what we want the user to pass in)
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Setting up our connection
while True:

    try:
        connection = psycopg2.connect(host='localhost', database='mark',
                                      user='mark', password='@Kezeji99', cursor_factory=RealDictCursor)
        cursor = connection.cursor()  # use to execute sql statements
        print("Connection established")
        break  # if we succesfully connect to the database we break out of the while loop, if we fail it goes back into that loop

# if connection fails and we get an exception - we get the error and store in a variable called error
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        # waits for two seconds before reconnecting, for a failed passwd it's never gonna reconnect, if it's internet or db having not fully initialized..
        time.sleep(2)


# path operation/ route
@app.get('/')
def root():
    return {"message": "Welcome to my API"}


# Retrieving a bunch of social media posts from our application
@app.get('/posts')
def get_posts():
    # using the object cursor from our connection to make a query
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    # print(posts)
    return {"data": posts}


# creating a post
@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    connection.commit()  # saves into postgres
    return {"data": new_post}


# Retrieving one individual post - id field reps a path parameter
@app.get('/posts/{id}')
def get_post(id: int):
    # converting the id a string again bec the sql code is in string
    cursor.execute(""" SELECT * FROM posts WHERE id= %s """, (str(id)))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}


# deleting a post
@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """ DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    deleted_post = cursor.fetchone()
    connection.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    connection.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")

    return {"data": updated_post}
