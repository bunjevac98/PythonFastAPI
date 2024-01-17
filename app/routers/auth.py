from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from ..utils import utils
from database.database import get_db
from .. import oauth2
from database import models
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.utils import utils

router = APIRouter(tags=["Autentification"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    # Create token
    # We putting this in payload
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
