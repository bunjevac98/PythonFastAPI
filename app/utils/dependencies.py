from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import oauth2, schemas
from database import models
from database.database import get_db


# Geting a document if exists
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = (
        db.query(models.Document).filter(models.Document.id == document_id).first()
    )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with ID: {document_id}",
        )

    return document


def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No project found with ID: {project_id}",
        )
    return project


# Geting project that have that document
def get_associated_project(
    document: schemas.Document = Depends(get_document), db: Session = Depends(get_db)
):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == document.project_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No project found with ID: {document.project_id}",
        )

    return project


def is_owner(
    current_user: dict = Depends(oauth2.get_current_user),
    project: models.Project = Depends(get_associated_project),
    db: Session = Depends(get_db),
):
    if current_user.id == project.owner_id:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access project documents.",
        )


def is_owner_or_participant(
    current_user: dict = Depends(oauth2.get_current_user),
    project: models.Project = Depends(get_associated_project),
    db: Session = Depends(get_db),
):
    if current_user.id == project.owner_id:
        return "owner"
    else:
        participant = (
            db.query(models.UserProjectAssociation)
            .filter(
                models.UserProjectAssociation.project_id == project.id,
                models.UserProjectAssociation.user_id == current_user.id,
            )
            .first()
        )
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access project documents.",
            )
        return "participant"
