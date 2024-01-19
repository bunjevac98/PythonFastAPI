from fastapi import (
    File,
    HTTPException,
    UploadFile,
    status,
    Depends,
    APIRouter,
)
from app import oauth2
from app.config import settings
from .. import schemas
from database import models
from sqlalchemy.orm import Session
from database.database import get_db
from app.utils import dependencies, file_utils


router = APIRouter(
    prefix="/document",
    tags=["Documents"],
)
BUCKET_NAME = settings.bucket_name
AWS_REGION = settings.aws_region


@router.get("/{document_id}")
def get_specific_document(
    document: models.Document = Depends(dependencies.get_document),
    project: models.Project = Depends(dependencies.get_associated_project),
    # access_type: str = Depends(dependencies.is_owner_or_participant),
):
    key = f"{document.project_id}/{document.file_name}"
    try:
        return file_utils.download_document_from_s3(document, key)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{document_id}")
def update_document(
    document: models.Document = Depends(dependencies.get_document),
    update_document=schemas.DocumentUpdate,
    current_user: dict = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
):
    try:
        print(update_document)
        document.file_name = update_document

        db.commit()
        db.refresh(document)

        file_utils.update_document_on_s3(document)

        return document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update the specific document: {str(e)}",
        )
