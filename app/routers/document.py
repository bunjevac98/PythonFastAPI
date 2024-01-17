from fastapi import (
    HTTPException,
    Response,
    status,
    Depends,
    APIRouter,
    Query,
    File,
    UploadFile,
)
from app import oauth2
from .. import schemas
from database import models
from sqlalchemy.orm import Session
from database.database import get_db


router = APIRouter(
    prefix="/document",
    tags=["Documents"],
)


@router.get("/{document_id}")
def get_specific_document(
    document_id: int,
    current_user: dict = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        specific_document = (
            db.query(models.Document).filter(models.Document.id == document_id).first()
        )
        """ logic that just owner of uploaded document can get that document
            we can check if the user is on that project where is document to-not implemented here
        if current_user.id !=specific_document.user_id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the document owner can get specific document",
            )
        """
        print(specific_document)
        if not specific_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document found with ID: {document_id}",
            )

        return specific_document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrive specific document{str(e)}",
        )


@router.put("/{document_id}")
def update_document(document_id=int, updated_document=schemas.DocumentUpdate,db: Session = Depends(get_db) ):
    try:
        # Query the database to get the specific document by document_id
        document = db.query(models.Document).filter(models.Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document found with ID: {document_id}",
            )

        # Update the document with the provided data
        for key, value in updated_document.dict(exclude_unset=True).items():
            setattr(document, key, value)

        # Commit the changes to the database
        db.commit()

        # Refresh the document to get the updated values
        db.refresh(document)

        return document
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update the specific document: {str(e)}",
        )