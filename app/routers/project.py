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
from typing import List
from app.utils import file_utils

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

# It is set that just owneer of project can upload file we need to change that


@router.get("/", response_model=List[schemas.ProjectBase])
def get_projects(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    projects = db.query(models.Project).all()

    return projects


# respones model
@router.get("/{id}/info", response_model=schemas.ProjectResponse)
def get_project(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id: {id} was now found",
        )

    return project


@router.get("/{project_id}/documents")
def get_projects_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    try:
        project = (
            db.query(models.Project).filter(models.Project.id == project_id).first()
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No project found with ID: {project_id}",
            )
        if current_user.id == project.owner_id:
            # User is the owner, proceed to get documents
            documents = (
                db.query(models.Document)
                .filter(models.Document.project_id == project_id)
                .all()
            )
            return documents
        else:
            # Check if the user is a participant in the project
            participant = (
                db.query(models.UserProjectAssociation)
                .filter(
                    models.UserProjectAssociation.project_id == project_id,
                    models.UserProjectAssociation.user_id == current_user.id,
                )
                .first()
            )
        if participant:
            documents = (
                db.query(models.Document)
                .filter(models.Document.project_id == project_id)
                .all()
            )

            if not documents:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No documents found for project with id--{project_id}",
                )

            return documents
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access project documents.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrive project documents: {str(e)}",
        )


# Maybe we should add owner_id for now because we dont have user
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProjectBase,
)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # id is now string
    print("this is user email:", current_user.id)
    # new_project = models.Project(**project.dict())
    new_project = models.Project(owner_id=current_user.id, **project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# We need user login info ?user=<login>
@router.post("/{project_id}/invite")
def invite_user(
    project_id: int,
    user_login: str = Query(..., alias="user"),
    current_user: dict = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    # Check if project exist
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with {project_id} not found",
        )
    # check if user that is loged in is owner of project
    if current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can invite participants",
        )
    # Checking if user we invite exist
    user_to_invite = (
        db.query(models.User).filter(models.User.username == user_login).first()
    )
    if not user_to_invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User to invite not found"
        )

    print("user to invite", user_to_invite)

    existing_invitation = (
        db.query(models.UserProjectAssociation)
        .filter(
            models.UserProjectAssociation.user_id == user_to_invite.id,
            models.UserProjectAssociation.project_id == project.id,
        )
        .first()
    )

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is already invited to the project",
        )
    new_invitation = models.UserProjectAssociation(
        user_id=user_to_invite.id, project_id=project.id
    )

    db.add(new_invitation)
    db.commit()
    db.refresh(new_invitation)

    return {"message": f"Invited {user_to_invite.username} to project {project.name}"}


@router.post("/{project_id}/documents")
def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        if not file_utils.allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX file are allowed",
            )

        project = (
            db.query(models.Project).filter(models.Project.id == project_id).first()
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with {project_id} not found",
            )
        # check if user that is loged in is owner of project
        if current_user.id != project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can invite participants",
            )

        s3_url = file_utils.upload_document_to_s3(file, project_id)
        print(s3_url)
        db_document = models.Document(
            project_id=project_id,
            file_name=file.filename,
            file_path=s3_url,
            user_id=current_user.id,
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        return {"messagee": "Document uploaded successfuly", "s3_url": s3_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


# We can update just name, description, logo, documents
@router.put("/{id}/info", response_model=schemas.ProjectBase)
def update_project(
    id: int,
    update_project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    project_query = db.query(models.Project).filter(models.Project.id == id)
    print(update_project)

    project = project_query.first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not autorized to perform requested action",
        )

    project_query.update(update_project.model_dump(), synchronize_session=False)

    db.commit()

    return update_project


# project.dict() is now dict(project) or project.model_dump()
# Proveritiii


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    project_query = db.query(models.Project).filter(models.Project.id == id)

    project = project_query.first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not autorized to perform requested action",
        )

    project_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
