from jose import jwt, JWTError
from datetime import datetime, timedelta
from app import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

# login is path from auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# Secret key
# Algorithm
# Exparation time

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    # We dont want to accidantly change data
    to_encode = data.copy()
    # Setting when jwt is expired
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # This is creating jwt token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# This function is called in get_current_user
def verify_access_token(token: str, credetials_exception):
    try:
        # Decoding JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract ID
        id: str = payload.get("user_id")

        if id is None:
            raise credetials_exception
        # Validate id or extra information if we have
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credetials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credetials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate credentials",
        headers={"WWW-Autenticate": "Bearer"},
    )
    # Returning token data who calls this action
    return verify_access_token(token, credetials_exception)
