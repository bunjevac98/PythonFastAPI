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
    access_type: str = Depends(dependencies.is_owner_or_participant),
):
    try:
        return file_utils.download_document_from_s3(document.file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{document_id}")
def update_document(
    document_id: int,
    current_user: dict = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
):
    # Fetch the existing document from the database
    existing_document = (
        db.query(models.Document).filter(models.Document.id == document_id).first()
    )
    if not existing_document:
        raise HTTPException(
            status_code=404,
            detail=f"No document found with ID: {document_id}",
        )
    try:
        # Upload the new file to AWS S3
        if file:
            # Specify the AWS S3 key for the new file
            s3_key = f"{existing_document.project_id}/{file.filename}"

            file_utils.update_document_on_s3(
                file=file,
                project_id=existing_document.project_id,
                existing_file_key=existing_document.file_path,
            )

            existing_document.file_path = s3_key
            existing_document.file_name = file.filename
            existing_document.user_id = current_user.id
            # Commit changes to the database
            db.commit()
            db.refresh(existing_document)

            return existing_document
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update document: {str(e)}"
        )


@router.delete("/{document_id}")
def delete_document(
    document: models.Document = Depends(dependencies.get_document),
    current_user: dict = Depends(dependencies.is_owner),
    db: Session = Depends(get_db),
):
    try:
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this document",
            )
        print(document.file_path)
        file_utils.delete_document_on_s3(document.file_path)

        db.delete(document)
        db.commit()

        return {"message": f"Document with ID {document.id} has been deleted"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)} ",
        )
