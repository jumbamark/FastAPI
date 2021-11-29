from passlib.context import CryptContext


# telling passlib what hashing algorithim we wanna use; bycrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hashed_passwd = pwd_context.hash(user.password)
def hash(password: str):
    return pwd_context.hash(password)


# logic of hashing the password from logins to see that it compares to the one in the db
def verify(plain_passwd, hashed_passwd):
    return pwd_context.verify(plain_passwd, hashed_passwd)
