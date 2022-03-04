# FASTAPI

uvicorn ORM.main.py:app --reload
ORM - Object Relational Mapper (layer of obstruction that sits between the db and our FastAPI) - ways of interacting with db
we can perform all db operations through traditional python code, no more sql
What ORMs can do;
instead of manually defining tables in postgres, we can define our tables as python models
Queries can be made exclusively through python code,no sql is necessary
ORMs - sqlalchemy (one of the most popular python ORMs)
It's a standalone library that has no association with FastAPI. can be used with any other python framework or app
pip install sqlalchemy

# specify our connection string - where our postgres db is loacted

SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>:@<ip-address/hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = "postgresql://marrion:Joyce98@localhost:5432/FastAPI" - before using env variables
when using env variable you include an f string

# create an engine - what's responsible for the sqlalchemy to connect to a postgres db

engine = create_engine(SQLALCHEMY_DATABASE_URL)

When you actually want to talk to the sql db we have to make use of a session
SessionLocator = sessionmaker(autocommit=False, autoflush=False,bind=engine)

Define our base class - all the models that we defined to actually create our tables in postgresare gonna be extending this base class
Base = declarative_base()
Create a file that will define all of our models; models.py

go to main.py;
code in the engine command - creates all of our models
create the dependency (db.py) - the session object is what's responsible for talking with the db. We create this function where we actually get a session to the db, every time we get a request we gonna get a session,we going to be able to send sql statements to it and after the request is done we close it out.

If you save your mmodels it creates the table in postgres
sqlalchemy generates your tables but it does it in a very simple manner, doesn't help in modifying tables(making changes to our tables/ migrations)

schema/pydantic model - Post model in main.py (refering in posts) - defines the structure of a request and response (ensures that when a user wants to create a post, the request will only go through if it has a "title", "content" etc in body - performs validation)
orm/sqlalchemy model - Post model in models.py (defines what our specific table(columns) in our db looks like)
schemas moved to its own file
In posts : Post replace Post with schemas.Post
create two different classes for eaach specific request - say you want the user to only update published,thats the field you pass in in the update class
create a postbase class and extend that class
replace schemas.Post with schemas.PostCreate

SENDING A RESPONSE BACK - just like we can define what a request should look like we can also define what a response should look like; what to return to user
In schemas.py create a class that handles response - within the decorator pass in a response model field

pydantic model only reads dicts, passing in the orm_mode(in response class) will make it read the response model even though its not a dict

response model is different in retrieving posts bec we're sending back a list of posts and it's trying to shape that into one individual post, to specify we want a list of posts we have to import sth from the typing library (List)

Creating user functionality - having users be able to create an account within our app, being able to login as well as being able to create posts that are asscoiated with their specific accounts
Handling user registration - enable users to create a new account ( define our model)

hashing the password when the user first registers to avoid storing it raw in the database
we install passlib which handles hashing in python and install it together with an algorithim((Bcrypt) pip install passlib[bcrypt]

create a utils.py - holds a bunch of utilities
extract all the hashing logic and store it in it's own function

Create a route that allows to fetch info about a user based off their ID;
it can be part of the authentication process (If you decide to set up JWT tokens to get send as cookies then the frontend may not know whether it's logged in or not)
retrieve a users profile if you wanna view it

# ROUTERS - used to split path operations to organize code

All our routers are in main.py - we create two separate files; for posts and users
create a route folder in ORM and create the two files
copy the routes for posts in posts.py and those for users in users.py
Link the routers to main.py file
add a router to individual files and add a prefix in the router to remove the path repetition (/posts/....)

localhost:8000/docs
Go to docs and group them accordingly based of their specific action (group titled posts, another titled users)
go to routers - post.py in route and add a tag (groups our particular requests into categories)

# AUTHENTICATION

Two main ways to taackle authentication;
session based authentication - we store sth on our backend server to track whether a user is logged in
JWT Token Authentication - it's state pass (there's nothing on our backend/API that actually keeps track or stores some sort of info whether a user is logged in or out), the token itself actually keeps track of whether a user is logged in or not

JWT Token Authenticatiom
Client -> API
User logs in: provides credentials > verify if they are valid ; if valid > create JWT token
we'll send a response back with the token
Client <- API
Client -/posts {token}-> API when app requires user to be loggged in to retrieve posts;he'll send a request to the /post endpoints but also provides the token in the header of the request > API verifies if token is valid > sends data
Token contains; header(algo and token type), payload(data), verify signature(combination of three things- the first two and our secret-only on our API, nobody knows it)

Create the login path
Since the user is going to be providing the login info it makes sense to create a schema that makes sure they provide valid data

Creating tokens
Define our function (create_access_token)
the access token is gonna have a payload, whatever data we want too encode into the token we have to provide that (of type dict)
make a copy of the data
create the xpiration field - provide the time of 30 mins from now (current time + 30 mins)
grab the copy of the dict and update it and pass in expiration and provide expire time - adding extra property into all that data we want to encode into jwt
call jwt and pass in everything that we want to put into the payload, secret key and algorithm
Go back to specific path operation
copy the jwt token and go into jwt.io to decode it

# retrieving user_credentials in our log in route - instead of passing in whatever we use a built in utility in the fastapi library (OAuth2Password..)

def login(user_credentials: OAuth2PasswordRequestForm = Depends, db: Session = Depends(database.get_db)):
user = db.query(models.User).filter(
models.User.email == user_credentials.email).first()

def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)) --> def login(user_credentials: OAuth2PasswordRequestForm = Depends, db: Session = Depends(database.get_db))
We set up a dependency kind of like we do with th db, this will require us to retrieve the credentials and fastapi will store inside the user_credentials variable
when we retrieve the users attempted credentials from OAuth2PasswordRequestForm, it's gonna store it in a field not called email but username we therefore should compare the models.User.email to user_credentials.username (which happens to be the email) because it returns two things( username= , password= )

When it comes to testing in postman we no longer send the credentials in the body, raw, we do it in the body,form data (pass in the key(username, password) and the values)
we logged in a user by sending a request to the login endpoint by providing a username and password and our API will then return an access token which the user can then use to retrieve data from our API, so any time he needs to access an endpoint or path operation that requires a user to be logged in he'll just send the jwt token and the payload and then our API has to validate the token

# VERIFY THE TOKEN IS STILL VALID AND HAS NOT EXPIRED

we are going to define a schema for the token
then create the verify token and get user function

what happens is any time we have a specific endpoint that should be protected (user needs to be logged in to use it) i.e you need to be logged in to create a post; we add in an extra dependency into the path operation function (.., get_current_user; stored in a user_id variable which will return an int and then pass in a dependency)
all this is saying is that this function is now gonna be a dependency, this is what forces the users to have to be logged in before they can actually create a post
the get_current_user function calls the verify_access_token and passing in the token which comes from the user, we gonna return the id which then gets returned by the get_current_user function and then in our post.py in our function we return the id and store it in a variable called user_id and then we can access the user id by printing it

You now cant create a post without authentication
to get authentication go to the login route and get the access token
go to create post > headers
create a header; Authorization is gonna be the key, and then the column is gonna be the Bearer space then paste in the token
or go to authoration then type in Bearer and paste in the token on the right
Now that we've protected our create_post route let's go ahead and do this with other routes;copying the dependency for get_current_user

This is gonna add a dependency which is gonna be that function that we created called get_current_user; any time anyone wants to access a resource that requires them to be logged in we except that they provide an access token

**_ if you want each of your path operations to fetch the user themselves they have th id from the get_current_user, though we can automatically do it under get_current_user; _**

we get the token data back (id), we need access to our database so that we can fetch the user
within the function we can pass in the dependency so that we can get access to the db object

# NAVIGATING THROUGH POSTMAN

create environment variables to avoid typing in the url
We can no longer just create posts bec of authentication, we have to copy access tokens to endpoints
we can do it through an automated fashion;
go to the login user endpoint and hit send to get a new acces_token
Through code we want postman to automatically set an environment variable;
go to tests and put in the code to set environment variables; pm.environment.set("variable_key", "variable_value");
Set the variable_key as JWT and the value as the access token
so how do we retrieve the access token from the login endpoint response; pm.environment.set("JWT", pm.response.json().access_token);
click send, the code will run and create a variable called access_token
Under create post instead of hardcoding we refernce the JWT variable; {{JWT}} - > in authorization
Any time we login a user it's going to automatically update

# RELATIONSHIPS

Relationship between users and posts;
create an extra column in our post table(User_id) and set up a special Foreign Key ( a foreign key is how we tell sql that a column(User_id) is connected to another table)
We specify the table that it should be connected to and what specific column it should use from that table;
Foreign Key, Table Users(id)
This is what is reffered to as a One to Many Relationship (one user can create as many posts as they want however a post can only be associated with one user)
In postgres;
add anew column to posts (user_id),make sure the data type matches the one in id from users table
go from columns to constraints to set up our foreign key constraints
under constraints go under foreign key
hit the plus sign and give the foreign key a name (posts_user_fkey)
to set the logic of the FK click the edit and go under columns to set up the relationship
provide the name of the local column (the column in our posts table)
its going to reference what table; the users table (public.users)
what column from the users table is it gonna reference; the id column of the user table
click add
Go under actions to set the on delete

SELECT \* FROM posts WHERE user_id=1;

set it though code in sqlalchemy;
create owner_id column, pass in Integer and Foreignkey()
pass in the exact table(reference the table name and not class name) and column that we wanna reference - users.id

There's an error when creating a post bec in the request schema we did not pass in the owner id;
we have to provide who the owner id is for any new post, we not gonna pass th owner_id in the body;whoever is logged in and creating the post should automatically be the owner
add the current_user.id into the new_post object in the create post endpoint

Rn if your logged in you can be able to delete any post

# Making sure that a user can only delete their own post

add an if statement about the owner_id and current_user.id

We have to be logged in to view posts, (if you want to return only the users posts)
On the frontend we wanna pass the users details instead of the owner_id;
For all the posts that we retrieve we would have to then send a second query to retrieve info for user with the given id
we can set it up in sqlalchemy so that it automatically does this for us
go t models and set up a relationship, it isn't a Foreign Key (does nothing in the database whatsoever), it tells sqlalchemy to automatically fetch some piece of info based off the relationship
we'll create an owner and use relationship to return the class of another model(User)
This will create another property for our post so that when we retrieve a post it's going to return an owner, it's going to figure out the relationship to User (it will fetch the user based off the owner_id and return that for us)

# QUERY PARAMETERS

Are optional key value pairs that appers to the right of the question mark, they allow us to filter the results of a request (maybe we want posts created in the last two hours);
go to post router > path operation where we are retrieving all posts. We want to let the user to be able to filter down on the posts that they want to see
Allow them to specify how many posts they want to retrieve all together
To allow a query parameter, go into our path operation function and just pass in another argument (limit: int = 10 (default value))
To send a query parameter, type in a question mark then grab the name of the query parameter which is limit
Set up our query so that it takes into account the limit
Send another query parameter called skip to specify how many we wanna skip
if you wanna be able to send more than one query parameter; posts?limit=2&skip=2
Set up a search functionality(based off the title) as the last query parameter;
{{URL}}posts?limit=2&skip=0&search=SECRET

#How to use spaces in search query; say you wanna search for "keep secret"
use percent which means space in your url
{{URL}}posts?limit=2&skip=0&search=Keep%S

## HIDING OUR CREDENTIALS

We should not hard code our db info into our code;
we are exposing our username and passwd,
we've set the url to go to our development postgres instance which is running on our local machine, when we deploy this to production our postgres server is not going to be running on this machine, it could be on a completely diff system, we would need a way for the code to automatically update and a production environment to point to the actual production postgres db instead of using the one that is hard coded in here (e.g under our oauth2 we have our secret key hard coded, this is sth we dont expose and we need it updated between our development and production environment because they may not be the same on both)
We use environment variables ( a variable that you configure on your computer(any application that is running on that comp will be able t access it))

#### {py -3 models.py} running in terminal

# SETTING ENVIRONMENT VARIABLES IN LINUX

creating an environment variable in linux; export MY_DB_URL="localhost:5432"
list of all env variables; printenv
how to acces a specific variable; echo $MY_DB_URL

With any project there's going to be a certain number of env variables;
what would be good is to perform some sort of validation to ensure that all of the right environment variables have been set for your application to actually run properly
when you read an env variable it's always going to come out as a string meaning you have to do all of the validation in code;
from pydantic library import BaseSettings
just like with any other pydantic model we can set up a class Settings
In there we can provide a list of all the env variables that we need setprint(settings.secret_key) (and even assign default values)
By setting it that way it's going to automatically perform all of the validation for us to ensure all of this have been set
create a variable called settings = Settings() - creating an instance of the settings class
we can now access those properties from settings; print(settings.secret_key)
If there's no default secret_key, it's going to check my system env variables to see if there's sth called secret_key, if there's none it throws an error
This helps to identify which environment variable is missing incase there are alot of them
for all of the settings and env variables create a separate file; config.py and move all of that code inti that file and in main.py import the instance of the class that we created(settings)

Now figure out what env variables we wanna use;

**_ the port is set to a string bec if we look at our db connection it goes into a url _**

Within our FastAPi directory create a new .env file which will contain all of our environment variables.
In production we are not gonna use it, in production we are gonna set it on our machine but in development it's okay to set everything there
We generally want to capitalize env variables but pydantic looks at everything from a case insensitive perspective
We didn't provide default values in our config
We now have to tell pydantic to import variables from our .env file
Inside the class ; (class Config:)
replace the credentials with the variables in the .env file
we have succesfully migrated all of our code to using environment variables. When we move to production we can just on the machine set all of these values that we have inside our config.py and it's going to automatically import it and update those values wherever wwe reference them

#VOTING/LIKE SYSTEM REQUIREMENTS
Users should be able to like a post
Should only be able to like a post once
Retrieving posts should also fetch the total number of likes
We should create a table for likes with a column referencing post id and another referncing id of user who liked the post

Composite keys - primary key that spans multiple columns (it does not care if there's duplicates in one column, it does not care if there's duplicates in the other column, all it cares is if both columns same in two different rows) - there should be a unique combination
since PK must be unique, this will ensure no user can like a post twice

Creating a likes table in pgAdmin;
go under table, create a new table and call it likes
Under columns add a columns; post_id(references id of specific post), user_id - select primary key for both (that's gonna create that composite key)
set up the foreign keys as well; those two are gonna reference other tables (for post_id go to constraints > foreign key)
Drop the table
Define the table in sqlalchemy

Setting up a vote route;
path - "/vote".
user_id will be extracted from JWT token.
Body will contain post_id and like direction (unlike or like).
vote direction of one means we are liking, 0 means otherwise.
In our routers folder create vote.py (don't forget to wire it up in main.py)

set up a decorator (post operation bec we have to send some info to the server)
Def a function (like), since we expect the user to provide some data in the body it usually means we want to define a schema to ensure they send us the exact info
schema for our liking; create a class called vote > first field should be a post id of type int > direction(integer as well - 0 or 1) - we should validate to ensure it's only zero or one (import conint from pydantic automatically and pass in less than or equal to 1)

# JOINING INFO FROM TWO TABLES

SELECT _ FROM posts LEFT JOIN users ON posts.owner_id=users.id;
SELECT title,content, email FROM posts LEFT JOIN users ON posts.owner_id=users.id;
SELECT posts.id, email FROM posts LEFT JOIN users ON posts.owner_id=users.id;
SELECT posts._, email FROM posts LEFT JOIN users ON posts.owner_id=users.id;
We're dealing with two tables, the first table referenced(posts) will be on the left while the second will be on the right
It compares the values between the two columns that we have selected(posts.owner_id=users.id), if the values match the LEFT JOIN creates a new row that contains the columns of both tables. If they dont match the user info will be set to null

SELECT posts.\*, email FROM posts RIGHT JOIN users ON posts.owner_id=users.id;
LEFT JOIN will show you instances where something that exists in the left table but doesn't exist in the right table,RIGHT JOIN does otherwise.

Getting number of posts by each user;
SELECT users.id, COUNT(_) FROM posts LEFT JOIN users ON posts.owner_id=users.id GROUP BY users.id; - will list only those with posts
SELECT users.id, COUNT(_) FROM posts RIGHT JOIN users ON posts.owner_id=users.id GROUP BY users.id; - will list also those without posts but counts null entries
SELECT users.id, COUNT(posts.id) FROM posts LEFT JOIN users ON posts.owner_id=users.id GROUP BY users.id; - wont count columns that have a null value (accurate)
SELECT users.id,users.email COUNT(posts.id) as user_post_count FROM posts LEFT JOIN users ON posts.owner_id=users.id GROUP BY users.id;

# WORKING WITH OUR POSTS TABLE AND OUR LIKES TABLE

SELECT _ FROM posts LEFT JOIN likes ON posts.id=likes.post_id;
SELECT _ FROM posts RIGHT JOIN likes ON posts.id=likes.post_id;

TOTAL number of likes for each post (counts the votes per post);
SELECT posts.id, COUNT(_) FROM posts LEFT JOIN likes ON posts.id=likes.post_id GROUP BY posts.id; - everuthing else without two posts has a value of one which is not correct(it counts null values as 1). to correct this(grab any column that is null and pass it in COUNT);
SELECT posts.id, COUNT(likes.post_id) FROM posts LEFT JOIN likes ON posts.id=likes.post_id GROUP BY posts.id;
SELECT posts._, COUNT(likes.post_id) as likes FROM posts LEFT JOIN likes ON posts.id=likes.post_id GROUP BY posts.id;

Querying for an individual post to get all the info + the total number of likes;
SELECT posts.\*, COUNT(likes.post_id) as likes FROM posts LEFT JOIN likes ON posts.id=likes.post_id WHERE posts.id=1 GROUP BY posts.id ;

# PERFORMING JOINS USING SQLALCHEMY

Retrieving a post with number of likes using sqlalchemy
When we retrieve a post FastAPI should send the number of likes as a property;
posts router > get_posts path operation
create a results variable
results = db.query(models.Post) #selscts every colum and then renames it accordingly, it gets that from the posts table. It's getting every single post
next step is to perform a join and specify (the table we wanna join, column that we perform a join on) - by default it's going to be a left inner join
results = db.query(models.Post).join(models.Like, models.like.post_id == models.Post.id)
We've been ignoring the keyword so by deafult it's been taking the OUTER but sqlalchemy has INNER as it's default. We want an OUTER though
results = db.query(models.Post).join(models.Like, models.Like.post_id == models.Post.id, isouter=True)
Next thing we have to do is to group by posts.id the perform the count on Likes.posts_id; group_by(specify the specific columns)
results = db.query(models.Post).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id)

Get the COUNT
import a function; from sqlalchemy import func (gives us access to functions like count)
results = db.query(models.Post, FUNC.COUNT(MODELS.LIKE.POST_ID)).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
When you print results it's named as count 1, we wanna change that to sth we will understand; total_likes
results = db.query(models.Post, FUNC.COUNT(MODELS.LIKE.POST_ID).LABEL("TOTAL_LIKES")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id)
perform the query by adding .all() and then return the results
We get errors( no title, no content, no time_posted...) - these are all pydantic validations. It's happening bec we used the response model of schemas.Post
If we go scemas > Post class - there's values it expects and none of them have been set
Remove the response model
This is what it returns under results [{{URL}}posts] ;
`[ { "Post": { "title": "Life Lesson 4", "published": true, "owner_id": 2, "content": "Sing in the SHOWER", "id": 4, "time_posted": "2021-11-25T10:30:16.729899+03:00" }, "total_likes": 0 } ]`

What it returns under post;
[
{
"published": true,
"title": "Life Lesson 10",
"owner_id": 2,
"id": 10,
"content": "Keep it SIMPLE",
"time_posted": "2021-11-25T12:44:55.626170+03:00"
}
]
This is what pydantic expects, it expects to get an object with a field of published,title.... however after our join something odd happens, we have a field called Post and that breaks everything bec it doesn't expect the id and the published and the owner to be under that dict.

To fix this we go to schemas and create a new schema; # Response - return results
Try to match the dict as close as possible
class PostResults(BaseModel):
Post: Post #Post of type Post(refernce # Response - return posts) - all those fields will be under a field named Post
total_likes: int

Go to posts.py and refernce PostResults;
[
{
"Post": {
"title": "Life Lesson 4",
"content": "Sing in the SHOWER",
"published": true,
"id": 4,
"time_posted": "2021-11-25T10:30:16.729899+03:00",
"owner": {
"id": 2,
"email": "allie@gmail.com",
"time_created": "2021-11-22T23:29:24.209381+03:00"
}
},
"total_likes": 0
}
]

Go ahead and add our filters back in; [ {{URL}}posts?limit=2&skip=0&search=Keep%SI ]

results = db.query(models.Post, func.count(models.Like.post_id).label("total_likes")).join(models.Like, models.Like.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()

update the get specific post to get the vote count also

# DOING MIGRATIONS IN SQLALCHEMY

When it comes to building out the table or the database schema, sqlalchemy has a little but of limitations (it doesn't allow us to modufy tables, create extra columns, add FK constraints) that's bec when we define this models sqlalchemy checks to see if the specific table name already exists, if it does it's not gonna touch it
Alembic(database migration tool) fixes this - it's able to allow us to create increamental changes to our database and actually track them

Developers can track changes to code and rollback code easily with GIT. We can do the same for databases and models/tables. Database migrations allow us to incrementally track changes to database schema and rollback changes to any point in time
We will use Alembic to make changes. It can also automatically pull database models from sqlalchemy and generate the proper tables

install the library; pip install alembic - gives access to the alembic command
alembic --help
Drop all the tables
alembic init --help
We have to initialize alembic; alembic init {directory name - alembic} - it will create an alembic directory for us - also creates alembic.ini file
go to alembic > env.py file

To the file add;
Bec alembic works with sqlalchemy and the models that we build with sqlalchemy, we need to make sure it has access to our Base object in models.py - it has to be from models(which is technically importing from database) and not database, by doing it from models it will allow alembic to read all of the models(doing it directly from database will not work) (import Base object into env.py) -- from ORM.models import Base (kinda gives us access to all of those sqlalchemy models)
For target_metadata(target_metadata = None) replace None with Base and grab metadata (Base.metadata)

Go to alembic.ini ( Please edit configuration/connection/logging settings in '/home/mark/dev/FastAPI/alembic.ini') ;
we have to pass one value (the sqlalchemy url - what's the url to access our postgres db)
sqlalchemy.url = driver://user:pass@localhost/dbname
replace with;
sqlalchemy.url = postgresql+{whatever driver you are using}://user:pass@localhost/dbname
If you don't provide the driver it uses whatever the default driver is. We are using {psycopg2}- you dont actually need to provide it but you can
Replace user, password and dbname with actual values
You can provide the port after local host if you want to; sqlalchemy.url = postgresql+psycopg2://livramento:kavayaMam@localhost:5432/SlowApi
At this point alembic is set up and ready to run however we should'nt hard code our data in our code (If we move into our production serverit's not gonna work properly bec they are not gonna use this credentials or this IP)
we then should overwrite those values with whatever is stored in our env file;

Under the config variable in our env.py file we should set a new option ;
config.set_main_option("value we are gonna override-sqlalchemy url in alembic.ini", "pass in our string")
config.set_main_option("sqlalchemy.urli", "postgresql+psycopg2://livramento:kavayaMam@localhost:5432/SlowApi")
cut the string in alembic.ini (leave it blank; sqlalchemy.url =)

Just like in the database.py use the settings object in the env file; from ORM.config import settings
override the credentials

When we want to make a change to our database we create a revision. The revision is what really tracks all the changes that we make on a step by step basis.
alembic revision --help ( theres a - m that allows us to add a message like in git)

alembic revision -m "create posts table"
It willl create a file under the versions. The versions folder under the alembic folder is going to contain all of our changes
The file created has two functions in revision identifiers
The upgrade function when we run the upgrade, it runs the commands for making the changes that we wanna do (in this case we wanna create a post able table; we put all the logic for creating a post table within this function)
If we ever wanna rollback we have to put all the logic in the downgrade function to handle removing the table.
Upgrade handles the changes and the downgrade handles rolling it back. It's all manual; you have to define how to do all of that.

setting up the upgrade function and configuring all the necessary columns for our post table
access the op object from alembic;
op.create_table("name of table", define our columns -> sa.colum(...))
Logic for undoing this changes;
op.drop_table("name of table")

To see what the current revision is; alembic current
alembic upgrade --help;
We have to provide a revision number to tell alembic what version of our db do we wanna go to.
To run the upgrade we provided in the function we should provide the revision number.
alembic upgrade fa80de2a2383 - it creates the post table and alembic_version table (what alembic uses to keep track of all the revisions) - don't delete

say we wanna add the content column;
alembic revision -m "add content column to post table" - it's gonna create a brand new revision.
Once again we have to put in the logic for upgrading and dongrading
now that we have more than one revision there's also a down_revision in the newly created revision.
Put in the logic for adding a brand new column for content; op.add_column..
every time you set up an upgrade function you have to set up a downgrade table(table, actual column)
alembic current (current revision) - where we created our post table
alembic heads - [61b660fb4e8c (head)] (Latest revision) - new one we just created.
alembic upgrade head/{revision number} -> Running upgrade fa80de2a2383 -> 61b660fb4e8c, add content column to post table

How to roll back;
alembic downgrade fa80de2a2383 - rolling back to revision
alembic downgrade -1 (goes back to one revision earlier) - removes content column

Creating a users table .
set up a new revision; alembic revision -m "add user table"
we get a new revision; set up upgrade and downgrade
alembic current.
alembic history - see history of our revision
alembic heads.
alembic upgrade head
alembic upgrade +1

After adding the user functionality;implement the relationship between users and posts- set up the foreign key that links user table to post table;
alembic revision -m "add foreign key to post table";
First we have to add a column to our post table called owner_id
We've created the column now we have to set the link between the two tables (Foreign Key constraint)
op.create_foreign_key("{name of fk}",{source table of the fk-fk for posts table}, reference the remote table(referent_table)-users table, specify the local column that we are gonna be using-column in the posts table, the remote column in the users table, ondelete)
set up the downgrade. - undo those changes
alembic current
alembic heads.
alembic upgrade head
Check in postgres to confirm the foreign key.

Create a new revision to add all the columns in post table
alembic revision -m "add last few columns to posts table"
alembic upgrade +1

Generating the likes tables.
We are not going to manually create it, we make use of the auto generate feature - using alembic to figure out what exactly is missing from our database, it takes a look at all of our models, it's going to import all of our sqlalchemy models and based off of the columns that we have set here it's going to figure out what our db is supposed to look like.
Regardless of what our db is in it's current state, we don't need to delete and build from scratch, it will update if sth is missing and make changes (it will figure out the diff between sqlalchemy models and our postgres db) - look at the time created changes on nullable field

alembic revision --help
alembic revision --autogenerate -m "auto-like"
alembic upgrade head

Adding a phone number column on user table;
alembic revision --autogenerate -m "add phone number"
alembic upgrade head - it's gonna push out those changes

IN MAIN.PY;
Since we have alembic,we no longer need this command in our main.py file- it's the command that told sqlalchemy to run the create statement so that it generated all of the tables when it first stated up
models.Base.metadata.create_all(bind=engine)
keeping it in will not break anything, but if it does create the tables for you then your first alembic migration isn't gonna have to do anything bec everything is already there

we've been testing our API by sending requests from postman (when you use postman you are actually sending a request from your own computer). Your API though can get requests from diff types of devices;computer,server,mobile devices and more importantly from a web browser using js fetch API.
When a web browser sends requests using js fetch API there's gonna be a slightly different behaviour that we have to account for which we cant take into consideration when using postman bec postman isn't a web browser;
Go to dev tools on google.com;
fetch("http://localhost:8000").then(res => res.json()).then(console.log)
It should print out the contents of whatever we get back from the server but we get an error; access has been blocked by CORS POLICY

# CORS POLICY - cross origin resource sharing

allows you to make requests from a web browser on one domain to a server on a different domain
By default our API only allows web browsers running on the same domain as our server to make requests to it

To fix this (if you wanna allow people from other domains to talk to your API);
In main.py ->
from fastapi.middleware.cors import CORSMiddleware (more in docs; CORS)
app.add_middleware(CORSMiddleware..., can allow specific requests and heaers too) . middleware is a term used in most web frameworks bec it's basically a function that runs before every request
If someone sends a request to our app before it goes thru the routers it goes through the middleware then the middleware can perform some sort of operation

We have to specify the origins that we wanna allow (what domains should be able to talk to our API) - create a list called origins of all domains that can talk to our API
If you want to allow all; "\*" - every single domain

# SETTING UP GIT FOR OUR PROJECT - so that we can start tracking our changes as well as set up a remote repo to store all of our code

Create a .gitignore file;
venv - we have no idea if someone cloning our repo is going to be using a virtualenv
create for them a requirements.txt file to know the packages they need installed; pip freeze > requirements.txt
cat requirements.txt - tells what version of every single dependency we need to install
for anyone that clons our repo all they have to do to install all of them; pip install -r requirements.txt

GIT
Setting up a remote repository so that we can store all of our code on github.
git init - it's going to initialize git
git add --all - it's gonna add all of the files that we have in our directory into git
Any time you add a file you have to commit it;
git commit -m "inital commit"
git branch -M main - it's gonna set our main branch to be called Main
Set up a remote branch - what's gonna allow us to store all of our code on github;
git remote add origin https://github.com/jumbamark/FastAPI.git (we're naming it origin, you can technically call it anything you want)
git push -u origin main - we are actually going to push all of our code upto github

At this point our repo is set up and we can move on to deploying our application.

# DEPLOYMENT

First of two deployment methods that we are gonna cover;
heroku login
heroku create --help
heroku create {app name-fastapi-mark}
git remote (shows all the remotes that have been set up for our git, there's two now - heroku and origin)
This is ultimately how we deploy our app, instead of doing git push origin main to push to github -> git push heroku main (pushes our code to the heroku platform it will then create an instance for our application)
git push heroku main
Our application has succesfully been deployed
gives us the url, copy in the browser - if you let it run long enough you are eventually going to see an errror
We pushed our code to heroku but heroku has no idea how to actually start our application.
when we deploy to our development environment, we ran uvicorn ORM.main:app but we haven't given that command to heroku
We have to create afile that is going to tell heroku the exact command that we wanna run;

## Inside root directory create a file called Procfile

Procfile just tells heroku what is the commmand that we need to start our application
we give it a process type and the command needed to run it (web-this is a web application that's gonna be responding web requests, uvicorn...)
we dont pass in the --reload flag bec this is production, we dont want it to automatically reload on changes bec there should be no changes.
We have to provide the host IP -> [--host=0.0.0.0 ]- we should be able to respond to requests from any IP
port flag (what port should we run this on) -> [--port=${PORT: -5000}] - if we dont provide a port flag then it's gonna default to port 8000. Heroku provides us a port,we dont know what it is ahead of time so we have to able to accept it regardless of what it is. It's going to pass this down as an environment variable. Any time you want to accept or reference an env var; ${} -> we want to take whatever value heroku gives us with the env var of port and we wanna assign it here. This is just giving a default value of 5000 if they dont provide one

After you make this file you then have to push out this changes to git once again
git status
git add --all/ git add .
git commit -m "added Procfile"
git push origin main
git push heroku main

Any timeyour application is not working on heroku;
heroku logs --help
heroku logs -t
There's an issue with settings which is the pydantic model that we've set up for achieving our env var. Theres validation errors for our settings model; no database_name,port..there's an issue with our env variables. It makes sense bec in development we use our .env file to provide all of the environment variables into that settings model and we pass that by specifying the env file.
We did not check our env file into git. We have to add those env variables either through the cpmmand line
Before we can do that we need to get a postgres db;
Heroku provides us with a free postgres instance that we can have access to -- postgres is one of their many add ons
heroku addons
Create a postgres instance;
heroku addons:create heroku-postgresql:hobby-dev --help
heroku addons:create heroku-postgresql:hobby-dev
Heroku is going to create our postgres instance - monitor in dashboard
click on it > settings > db credentials > view- there's an ip address, db name (they give us a fixed name),user, port
Go back to our application > settings > Config vars (it's where we actually provide env variables to our heroku instance)
there should be one that's added by deafult (URL)
We could go into our app and update our codeso that in the db.py file we could provide one specific url{settings.database_url} but NO
Instead of using the default env variable we are going to break it into multiple different environment variables;
Go into config.py and look at the env variables we need set
database_hostname
database_port
database_username
database_password

Now we set up those variables, how do we restart our heroku instance/dyno;
heroku apps --help (no access to restart)
heroku ps --help
heroku ps:restart
heroku logs -t
**_ heroku apps:info fastapi-mark _**

The app is up and working but trying to log in or creating a user raises some issues (Internal server error);
We deployed a brand new instance of postgres
create a postgres instance(servers > create > server) in pgadmin and connect it to the one in heroku by provide the same exact connection info
we have succesfully connected to our heroku postgres instance.
You'll see a tone of different databases; we wont be able to access most of these. The reson heroku is able to provide this for free is that they have one instance of postgres and then they give you one database within that instance that only you can access.
our db is d131h23r4n5576
go to schemas > public > tables and you'll find there is nothing in there
That's really the reason why our application is not working; we have a brand new postgres instance but we havent actually set up our schema or tables.
This is where alembic comes into play once again. Since we already have all of our revisions set up, getting our production database to match our development database will be as simple as running one command

In our development environment we use alembic to manage our db schema (alembic was responsible for creating all of those tables, since we have all the revision files we can essentially track all the changes that we make)
to get our development db upto date we run;
alembic upgrade head - goes to latest revision and make sure our postgres instance matched whatever that is
In our production database,we'll run the same on our heroku instance
bec we've tracked alll the files to git then our heroku instance has access to all of our revisions.
So when we run alembic,it can keep track of all of those changes as well in our production server
We never run alembic revision on our production server

How do we run a command in our heroku instance;
heroku run <specific command that we wanna run>
heroku run "alembic upgrade head"
Not only did it get our postgres instance upto the latest revision, it has all of the other increamental steps added in as well. We can roll back to any of them just like we did in development.
Go back to pgadmin and refresh tables. They are all there now

heroku ps:restart

HOW DO WE PUSH OUT CHANGES TO OUR APPLICATION
Make whateve change
Push out those changes to the git repo first;
git add .
git commit -m "modified steps.txt"
git push origin main
git push heroku main

DEPLOYING OUR APPLICATION ON AN UBUNTU SERVER
You can host your ubuntu serverand run it on any of the major cloud proviiders;AWS, Azure, Digital Ocean, local machine, rasberry pi
Digital ocean;
Get started with a droplet > Ubuntu > CPU options: Regular intel with SSD > select your data center > host name > Create droplet and digital Ocean will ceate our ubuntu vm
You shoul see a public IP; IP we'll use to connect to our virtual machine
Terminal;
ssh <username that we wanna connect to the device>; ssh root@<ip address/ip> ; yes
password - passwd provided when we created the virtaul machine
we are now succesfully logged in to our ubuntu virtual machine
Any time you get a brand new ubuntu virtual machine we wanna update all of the installed packages
install pip > use pip to install virtualenv (sudo pip3 install virtualenv)
install postgres
psql -U postgres
Peer authentication - default config for postgres (takes user that's logged in to the ubuntu machine and it tries to login as that user) failed
Changing postgres password for a certain use;
\password mark

cd /etc/postgresql/14/main
ls > open up postgresql conf > sudo vi postgresql.conf
Under CONNECTIONS AND AUTHENTICATIONS Take a look at the default config ; under listen addresses it;s only going to allow localhost to connect to ourdatabase (only when logged in into this Ubuntu VM can we the log in to the database). You wanna change this but it's not necesssary
listen_addresses = "\*"

Getting rid of peer authentication;
next file: sudo vi pg_hba.conf;
change from peer to md5

# IPv4 local connections:

Unblock remote connections from local host (127.0.0.1/32) to any ip address (0.0.0/0)- means any IP address
Do the same for IPv6; change to ::/0 - syntax in IPv6 for saying any IP address
save changes: (:wq)
Till now we are logged in as the root user; we are going to create another user with root privileges;
adduser jumba_mark
su - jumba_mark (This user by default does not have root access); usermode -aG sudo jumba_mark
make a folder to store our app > mkdir app > cd app > virtualenv venv > ls -la
create another folder called src (will contain all of our source code) > copy all of our code onto the VM
it's already stored on github > go to the url for our repo

CLONING FROM GIT;
git clone https://github.com/jumbamark/FastAPI.git . (hitting space dot will install in this current directory, it's not going to create another directory that's the name of my repo)
cat requirements.txt - tells what version of every single dependency we need to install
pip install -r requirements.txt

Setting env variables on linux machine;
cd ~
create a file; touch .env
open it up ; vi .env
provide a list of all the environment variables; export DATABASE_NAME = mark
source .env - sets all the env variables
printenv
cat .env

Method 2 ; copy all the env variables and save them in .env file without the word export before them
set -o allexport; source /home/mark/.env; set +o allexport
printenv

If we reboot (sudo reboot) we lose all of our variables that we set (we need to get them to persist the reboot);
cd ~
la -la
go into .profile file > vi .profile > Go to bottom of file and paste; set -o allexport; source /home/mark/.env; set +o allexport > :wq

cd src > alembic upgrade head - going to set up our database and it's going to update it to the latest revision
uvicorn --host 0.0.0.0 app.main.app --help
uvicorn --host 0.0.0.0 app.main.app (listening on any ip that this machine is potentially running)
right now if this program crashes or if we reboot it doesn't actually restart automatically
we'll use a process manager: gunicorn > pip install gunicorn
gunicorn --help (set up the number of workers- we'll set up 4 by default)
gunicorn -w 4 -k uvicorn .workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

We want it to run in the background (not terminal) and automatically start up on boot
We are going to create our own servers which start the application for us.
cd /etc/systemd/system/ > ls to view all the services installed on our machine
We are gonna create a brand new one (gunicorn_service file,- hour 11:50)
Create a service in system; sudo vi api.service and paste in all the contents of gunicorn.service.
systemctl status FastAPI - should give us the status of our service
The service created does not have access to users env variables > pass in another field in gunicorn_service (Environment file)
systemctl daemon-reload
systemctl restart FastAPI
systemctl status FastAPI

Automatically start upon a reboot; sudo systemctl enable FastAPI

NGINX -intermediary web server-running on our ubuntu vm,will receive the original request and act as a proxy
High performance webserver that can act as a proxy. Can handle SSl
HTTPS Request --> NGINX --> GUNICORN
Setting up nginx; sudo apt install nginx -y
systemctl start nginx (default config file - server block)
ls > cat default
open up the default file and replace the location with what we have in nginx file

Right now our browser is saying not secure - we are using http and not https, we need to set this up for https
you need a domain name
Point domain name to digital ocean
Under the name service section > custom DNS > point it to the DNS service of digital ocean
In digital ocean > dashboard > manage DNS in digital ocean > enter your domain
create an A record and CNAME also

We can set up ssl- we can handle secure https traffic
search for certbot
Make sure nginx has been set up to automatically start upon a reboot; systemctl stauts nginx > systemctl enable nginx (if set to disabled)

Set up a firewall on our machine - for basic security purposes (wanna make sure we only open ports that we're gonna be using)
Use the built in firewall called ufw > sudo ufw status
Set up a bunch of rules > tell the firewall what kind of traffic should we allow to our machine > sudo ufw allow http/https/ssh/5432
sudo ufw enable
sudo ufw status

Making changes;
push to github then go to our application;
cd FastAPI/app/src
git pull
pip install -r requirements.txt (if we had changed it)
sudo systemctl restart api

# DOCKERIZING OUR APPLICATION;

How to set up our FastAPI environment within our docker based environment
How to set up a postgres database within docker;
Install docker on your machine
Create a Dockerfile; will have all of the steps necessary to create our own custom image
copying everything at the end
When docker runs,when we build images from an docker file it actually treats each one of the lines/steps as a layer of the image
It caches the results of each step, when you cache the result if nothing changes we can just use the cached result

DOCKER COMPOSE - use to automatically spin up our containers with the desired configuration
We wanna use docker compose instead of docker run;
docker compose does the same thing as running docker commands on the CLI, we just provide all the instructions on a file so that we don't have to remember all the long commands with extra flags
Provide a set of instructions in a file called docker-compose.yml (It's a yamo file-markup language)
docker-compose --help
Run the file: docker-compose up --help
docker-compose up -d (we are rebuilding our image because we specified build in docker-compose, then it's going to start our container, it has the number one because there is one instance but if i told it to spin up 4 then we'd have 4)
docker ps
docker ps -a
docker logs fastapi_api_1

Pass in the env variables
docker-compose down (to tear everything down)
docker-compose up -d (It doesn't build the image this time-goes to docker image and looks for the image it would have created)

# SETTING UP OUR POSTGRES DATABASE

Create a brand new service (another container) for running our postgres database
figure out the ip address;

Set up the database first using depends_on;
docker-compose down
docker-compose up -d

Docker container challenges from a development perspective;
Make a change(in main.py) and realize it's not effective.
docker ps
We wanna see what the file system of FastAPI looks like;
docker exec -it fastapi_api_1 bash (it's gonna enter into interactive mode,specify the container name then type in the word bash)
We get a linux prompt;
cd ORM
cat main.py (print out the content of main.py)

The changes didn't get pushed out to the container;
we make use of a special volume called bind mount - it allows us to sync a folder on our local machine with a folder in our container
Define a volume under volumes
docker-compose down
docker-compose up -d
Add --reload in the docker file/ overwrite it in docker-compose

Create an account on docker hub; It's the docker equivalent of github
We'll create aa repo so that we can actually store our images here and track changes over time
docker image ls
pushing it to docker;
docker push --help
docker login
docker push jumbamark/fastapi:tagname
docker image tag --help
docker image tag fastapi_api jumbamark/fastapi_api
docker image ls
docker image tag fastapi_api jumbamark/fastapi
docker image ls
docker push jumbamark/fastapi

When we move to production,assuming we are using docker in production we can't use this docker compose file; the env variables will need to change and we can't hard code then, we wouldn't want the reload flag, no bind mount bec the code shouldn't be changing in production, ports could be different. There are some differences in docker env (dev and prod) we nedd to account for that;
create two docker compose file - for development and production
docker-compose down
Making changes to the docker-compose prod
starting up docker will be different now
docker-compose -f docker-compose-dev.yml up -d

In a production environment you dont ever wanna buuild the image in prod env; when you done developing you push the brand new image to docker hub
In prod you just pull this image from docker hub; remove the build from prod file and set it to image

Stop your containers;
docker-compose -f docker-compose-dev.yml down

Currently whenever we make new changes we have no idea if those changes break functionality in our code;
AUTOMATED TESTING LIBRARY
library we are going to use: pytest
pip install pytest
pytest (type it in to run our tests)
Create a test directory > create mytest.py
Create a file(calculations.py) to create a function to test, our project has advanced for testing
Testing - you ran the code with some test data, and you know what the result should be cause you created this data and make sure the result of the code matches with your expected results
Within tests folder you nid to have **init**.py to make it a python paackage
Test file should start with test_py or \_test for it to be identified by pytest (auto discovery of files) or
pytest tests/test_calculations if you don't want to use auto discovery
naming does matter(in test_calculations.py), it should start with test
pytest --help
pytest -v (instead of having a dot it lists out the specific test that's running)
pytest -v -s (s flag is for printing out statements-pytest does not print out any of your print statements by default)

Create a few more dummy functions that we can use for testing before going into advanced testing
Pytest provides some tools to minimize amount of repetitve code; fixtures-function that gets run before the specific test that you want

Any time we throw an error we are automatically going to make the test fail
For scenarios where we expect to receive an error we need to create a different test case
In real code you wouldn't just throw generic python exception you gonna usually create your own exception classes; InsufficientFunds
Benefit: for some reason our code raised another type of exception it would consider this test as failing

TESTING OUR APPLICATION
When it comes to fastapi it automatically provides us a test client
create test file for users > import from our app package(main file), import FastAPI instance so that we can test it

Test the the simple route path > call it test_route > we're sending a get and the url: route path
pytest -v -s tests/test_users.py

Other flags that can be passed to the pytest command;
pytest --disable warnings
When you have multiple tests fail (you want it to stop when the first test fails) - pass in the x flag
pytest --disable warnings -v -x

tests to create a user - the only difference is that since we are now sending a request to create a user we have to send data in the body
To confirm the test works, go to the database and you'll find the data passed in counts as a user

We are using our development database for our tests and that's not good,we need to create a separate db;
In db.py we've actually set up a dependency which returns the session local that alllows us to make queries using sqlalchemy
How to set up;
copy the contents of db.py intotest_users
replace get db with override_get_db
How exactly do we ovveride the db or any dependency --> fastapi docs (Testing Dependencies with Overrides, Testing a Database);
app.dependency_overrides[get_db] = override_get_db = in our functions any of our routes we've got Depends(get_db) we we ran this ovveride it's gonna slop it out with the function that we have under test_users with the function we replaced which is just going to give a different section object which can point to another postgres database
create another database; fastapi_test and reference it in test_users
the db has no tables;go to main file and copy the engine that will tell sql alchemy to build all the tables, based off of the models. We could use alembic as well
Our test database is now set up, when we run our first test it will run "Base.metadata.create_all(bind=engine)" the which should create all of our tables for us

pytest --disable-warnings -v tests\test_users.py -s

The user is now set up, we have now gotten our test database set up so that we can no longer interfere with our development database. Your test database does not have to run on your local machine, you can run it anywhere; on a docker container, remote machine
When we run the tests again it breaks bec the user already exists and we trying to get a new user with the same exact email
Getting around this limitations; make use of fixtures- function that runs before your test runs
Before our code runs we can create some tables and then after our code runs we can drop our tables
Drop likes,users and posts in the tests db
pytest --disable-warnings -v tests/test_users.py -s
It drops the tables after we are done
Put drop tables at the top so that it starts with dropping tables - this way you"ll get to keep the tables after the func runs and it helps in troubleshooting (pass in the -x flag)

We can choose to use alembic instead of sqlalchemy;
from alembic import command

We can configure a fixture to be dependent on another fixture (essentially pass one fixture into an argument of another fixture)
We wanna have one fixture that returns our db object so if wanna ever manipulate data directly and another fixture that returns our clients
this one returns our client;

@pytest.fixture
def client():
Base.metadata.drop_all(bind=engine) # command.upgrade("head") # we can run our code before we run our test
Base.metadata.create_all(bind=engine) # command.downgrade("base")
yield TestClient(app) # return TestClient(app) # run our code after our test finishes # Base.metadata.drop_all(bind=engine)

But we want another that returns just a database object;
call it session and move the logic of deleting and creating our tables in session, copy the section in the override functionality and paste it into session
This session fixture is going to yield the db object
pass the session fixture into client fixture
Any time we go into one of our tests and pass in the client fixture as a dependency it's gonna call client which will call the session fixture before it runs
Copy all the override func into client, remove the db variable and instead of yielding db we gonna yield session
Do the override and then return a brand new test client that
The benefit is that not only do we get access to the client, if we want to we can also get access to the db as well by passing in session in our test funcs and make queries; session.query(models.Post..). Now we have both access to the db object and client

We can actually remove the ovveride that's not within the fixture and the create all cause we are doing it all within the fixtures now

Our test users file is a little bit cluttered with all of this db info; move all of our db specific code to another file (database.py under our tests folder, including the fixtures as well)
Import the client and session fixtures into test_users

Set up the test for login - we dont nedd the trailing slash because there's no prefix,we don't send the data in the body (if you go to postman we do send it in the body but as form-data and not json). The field for email is actually called username
There's an issue bec we get a brand new database every single test that we run (fixtures have two scopes and we are using the default one which runs before any test) .So the user won't be present for the thirs test which will make it fail. (pytest docs > fixtures > scope)
We should change the scope from the default to module (will run once and be used by the tests in test_users modules) in db.py
It still creates an issue bec the login test is there dependent on the create user test; it's bad practice to make tests be dependent on other tests
Change back the scope to function which is the default value bec we want to load up a brand new db by dropping our tables and then creating new ones every single time we ran our tests.
To make our login user test independent of any other tests so it's not reliant on a specific order; before our login user test runs we want to actually go and define a function that will get called that will actually create a brand new user so that we can actually test the login in app
Create a fixture that will create a test_user for us;
def a test_user fixture (responsible for creating a test_user), it will make a call to our create user route. We need access to client or session object
Define a dict with the data that I'm gonna use for my users
Not only do we want to create a test user, we wanna actually return info about the user so that this login user will have the correct data to send when he tries to login
Return nothing and pass in the test_user(into login user test) so that also runs
Now the login user test is dependent on two different fixtures: the client and test_user
Incorporate password into res.json so that the data returns the password (using the new_user varaible)
Return new_user, so any time someone calls test_user or we have a test dependent on that, its gonna run the function and return the new_user
Now that we have the new user you can pass in the details(in login user test) by referencing test_user

Doing a little more validation for the login user route to make sure we got a token, the token is valid and do a few extra checks
Just like we did with test create_user we can make use of the pydantic model that we use for the response;
we will have to validate the token using the logic from auth2.py; decode the token

Create a special file under our tet directory (conftest.py - special file that pytest uses.It allows us to define fixtures in here).Any fixtures you define in the file wil be automatically be accessible to any of our tests within the test package. It's package specific.
take all of our database code and move it to conftest
By doing so the session fixture as well as the client fixture will all be accessible to any test files within the test folder automatically.
So we don't actually have to import anything
Move test user to conftest as well
pytest -v --disable-warnings tests/test_users.py -s

Create a login test for incorrect details by deliberately putting in the wrong password
we also wanna test the wrong email as well, and wrong email and password; we can use parameterize; also set the password and eamil to None- the schema validation will fail because it expects a username and password. We should get a 422

Create a file for posts tests
There's a challenge because all of our post path operations require authentication
HOW TO DEAL WITH AUTHENTICATION WHEN IT COMES TO TESTING
set up a fixture that automatically does this(login,get a token, make a request to posts) for us
instead of making a request to our APi import the auth2 method for creating an access token so we can import it into our tests, then create our own token without having to use the entire API
go to conftest and create a new fixture that's be dependent on test_user
Usse create user from oauth2.py which requires data passed in as a dict

create another fixture that gives an authenticated client - if we want to deal with any path fixture that requires authentication we can call the authorized client instead of the regular client
Update the headers because we need to pass the token inside the headers (pass in a dictionary: spread out all the current headers and then add one more which is going to be the authorization)
It's basically taking the original client and then just adding the specific header that we get from the token fixture
Printing json to see the data gives you an empty array bec there's no test posts in our database. Like we did with the login user where we created a test_user before we gonna have to do this with our posts, we need to create a whole bunch of posts and then verify that we are able to retrieve them;
create a fixture that will create a few initial posts;
pass in test_user bec without a user you cannot create a user,session bec we need to work with the database
Use sqlalchemy(session) to add all posts to the database;
You can hard code in the posts or use map which has a function that you created,it will iterate through the lists and it's going to take each item in the list which is a dict and it converts it into models.Post
make get_all_posts relient on test_posts
Adding a function into the test to use the schema result
pytest -v tests/test_posts.py -s

### deleting a post owned by someone else- more than one user, posts owned by multiple users

create a second test user
Add another post and assign in to user 2 then try deleting it when logged in as user 1

Updating post - define dict with values that you wanna update
SET UP A TEST FOR LIKES - create a test_likes.py file

# CI/CD PIPELINE

When it comes to adding new features and making changes to our code we have to go through a very manual process before we can get those changes pushed out to our production environment
What's good is setting up a CI/CD pipeline so that we can do all of this in an automated fashion
Continous Integration - automated process to build, package and test applications
Continous Delivery - Picks up where CI ends and automate delivery of applications (responsible for pushing out those changes to your production network)

Current Manula process;
make changes to code
commit changes
run tests - to verify that our changes didn't actually break any known functo=ionality to our code
Build images (docker images,if we happen to be running docker)
Deploy

Automated CI/CD pipeline;
make changes to code
commit changes
When you commit changes to your code that's going to trigger our CI/CD pipeline to run(our CI phase starts at this point)
CI phase;
pull our source code
Install dependencies
Run automated tests
Build images
CD phase;
grabs latest code or new build image
update production

Common CI/CD Tools - circleci, Travis Ci,github actions
We will use Github Actions for our CI/CD pipeline. It's already integrated with our Github repo and it's hosted on Github so there's no need to install anything on our local machine

CI/CD Tool
It provides a runner - computer(VM) to run a bunch of commands we specify
These commands are usually configured in yaml/json file or through GUI
The diff commands we provide makeup all of the actions our pipeline will perform
The pipeline will be triggered based off of some event (git push/merge)

Steps;
actions/checkout@v2 (tells machine to pull our code-after we do a git push)
actions/setup-python2v2 (set up python 3.9)
python -m pip install --upgrade pip (update)
pip install -r requirements.txt
pip install pytest
pytest (test with pytest)
We giving this steps to our vm so that it can run automatically after a git push

# SETTING UP GITHUB ACTIONS (github actions docs)

In our main project directory create a .github/workflows folder
Create a yamo file in workflows and give the workflow a name
Define when should our pipeline trigger > pass in the on build and specify should it be a push or a pull_request or should it run for both (push,pull_request, [push,pull_request])
You can specify the branches > go down level and on push define the branches;
on:
push:
branches: ["main", "anotherbranch"]
pull:
branches: - "test_branch"

Any time we do a push to either one of these branches it's gonna run our code and any time we do a pull request to this specific branch it's going to run our code

Once defining what's going to trigger our workflow we have to then create a job (set of steps executing on the same runner)
name of job > operating system > list of steps (under steps give the name(description) and uses(exact command))- Go to Github> Marketplace > checkout
You could specify the specific repo that you want to pull however github already knows what repo we're working on bec we do the git push and all of this is integrated together
after pulling the github repo, set up python (Marketplace > Setup Python)

when adding the pytest step the workflow will fail due to validation errors (there are no environment variables)
Setting our env variables in our workflow so that we can provide info for reaching our specific db;
job specific environment variables Github actions > env variables
work with gihub secrets to not expose the details of our env variables (github page > settings > secrets - define secrets that we can use and access in our workflows)
Another option; first remove the current repo secret then go to Environments option
We can create one for testing,development,production
Within the environment add a secret then in our job we can specify what the env is for the job

We have to set up a database for testing on the runner itself or we would have to point it to a remote database
setting up a test db on our runner;
create a service container - github actions allows us to spin up a docker container (Docs-Creating PostgreSQL service containers)
Creating a docker image and pushing to dockerhub;
to have docker working in our github workflow; (Docker docs - Confidure Github Actions)
set up a repo on dockerhub  
Generate an access token (github-actions)  
create a secret for both our username as well as docker hub access token;
Go to settings and put it in the previous testing environment
once you set it up,follow the steps to set it up in our yamo file
profile > account settings > security > new access_token

We have now succesfully completed our CI section of our CI/CD pipeline
The next step is to set up the continous delivery which is a matter of providing a whole bunch of commands needed to push out our new code to our production network
You can comment out all the docker steps(to make things as quick as possible) because we are not using docker in production (avoid using too many of our build minutes)
create another job for CD
jobs run in parallel so you need to pass in needs-list of jobs that need to complete before this job can run
deploy on heroku and ubuntu server
heroku;
pull our github repo
install heroku CLI
heroku login
add git remote for heroku
git push heroku main
Look for a built action in the github marketplace that does this all under the hood
heroku API key, heroku app name, heroku email - save the secrets in production environment
heroku profile > account setings > API key

Deploying updates to ubuntu server
login to ubuntu
cd /app/src
git pull
systemctl restart api
Marketplace > Built in action (SSH Remote Commamds)