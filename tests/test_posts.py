from ORM import schemas
import pytest


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostResults(**post)

    posts_map = map(validate, res.json())
    posts_list = list(posts_map)
    # assert posts_list[0].Post.id == test_posts[0].id

    # print(res.json())
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


# unauthenticated user is not able to retrieve all the posts
def test_unauthenticated_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthenticated_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


# post with id that doesn't exist
def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/330")
    assert res.status_code == 404


# try to retrieve a valid post
def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    print(res.json())
    # doing a validation
    post = schemas.PostResults(**res.json())
    print(post)
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content


# creating a post
@pytest.mark.parametrize("title, content, published", [
    ("Life Lesson 7", "Wave at the children on a SCHOOL BUS", False),
    ("Life Lesson 9", "Beware of the person who has nothing to LOSE", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published})
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    # assert created_post.owner == test_user["id"]
    assert created_post.title == title


# checking to see if a default value of True gets set for published
def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post(
        "/posts/", json={"title": "Arbitrary title", "content": "Arbitrary content"})
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.published == True


# testing if we are not logged in
def test_unauthenticated_user_create_posts(client, test_user, test_posts):
    res = client.get(
        "/posts/",  json={"title": "Arbitrary title", "content": "Arbitrary content"})
    assert res.status_code == 401


# unathorized user trying to deleting a post
def test_unauthorized_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


# testing a valid deletion
def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


# deleting a non-existing post
def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/123")
    assert res.status_code == 404


# deleting a post owned by someone else- more than one user, posts owned by multiple users
def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403


# updating posts
def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "published": False,
        # "id": test_posts[1].id
    }
    res = authorized_client.put(f"/posts/{test_posts[1].id}", json=data)
    updated_post = schemas.PostUpdate(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


# updating another user's post
def test_update_other_user_post(authorized_client, test_user, test_user2, test_posts):
    data = {
        "title": "The prime geeks",
        "content": "Nonnie-Lynne-Mark",
        "published": True,
        "id": test_posts[3].id
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403


# unauthenticated user trying to update a post
def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

# updating a post that doesn't exist


def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "The prime geeks",
        "content": "Nonnie-Lynne-Mark",
        "published": True,
        "id": test_posts[3].id
    }
    res = authorized_client.put(f"/posts/59", json=data)
    assert res.status_code == 404
