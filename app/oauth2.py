from jose import jwt, JWTError
from datetime import datetime, timedelta
from app import schemas
from database import models
from database.database import get_db
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings

# login is path from auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# Secret key
# Algorithm
# Exparation time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


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
        id_payload: str = str(payload.get("user_id"))

        if id_payload is None:
            raise credetials_exception

        # Validate id or extra information if we have
        token_data = schemas.TokenData(id=id_payload)

        print(token_data)

    except JWTError:
        raise credetials_exception

    return token_data


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credetials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Autenticate": "Bearer"},
    )
    # maybe to rename it
    token = verify_access_token(token, credetials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    # Returning token data who calls this action
    return user
