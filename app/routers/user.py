from fastapi import HTTPException, status, Depends, APIRouter
from ..utils import utils
from .. import schemas
from database import models
from sqlalchemy.orm import Session
from database.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# This need to be POST /auth
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with : {id} does not exist",
        )

    return user
