from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy .orm import Session
from .config import settings

# we provide tokenUrl (our login endpoint; auth.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY
# Algorithm
# Expiration time


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# access token function
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# function to verify the access_token (pass in token and specific credential exceptions - if credentials don't match)
def verify_access_token(token: str, credentials_exception):
    try:
        # print(token)
        # decode the token and store all of our payload data
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # extract the data;id (we get the specific field that we put in in the login route under access_token; "user_id; gets id of the user")
        id: str = payload.get("user_id")
        # If there's no id we're going to raise a credentials_exception
        if id is None:
            raise credentials_exception
        # if id then validate that it matches our specific token schema
        token_data = schemas.TokenData(id=id)
    # except JWTError as e:
    #     print(e)
    #     raise credentials_exception
    # except AssertionError as e:
    #     print(e)

    except JWTError:
        raise credentials_exception

# token data in this case is nothing more than the id
    return token_data


# function to get current user - we can pass this as dependency into any one of our path operations (takes the token from the request automatically, verify token is correct by calling verify_access_token, extract the id and then if we want to we can have it automatically fetch the user from the database and then add it as a parameter into our path operation)
# in Depends pass in the oauth2_scheme
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # define our credentials exception that we're gonna pass into the verify_access_token function  (when it's wrong or there's some kind of issue)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    # return verify_access_token(token, credentials_exception)
    token = verify_access_token(token, credentials_exception)
    # print(token)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
