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
from app.schemas import ProjectInvitationCreate
from database import models
from sqlalchemy.orm import Session
from database.database import get_db
from typing import List
from app.utils import image_utils, file_utils, dependencies, invitation_utils

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
    project: schemas.ProjectBase = Depends(dependencies.get_project),
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.get_current_user),
    access_type: str = Depends(dependencies.is_owner_or_participant_off_project),
):
    try:
        documents = (
            db.query(models.Document)
            .filter(models.Document.project_id == project.id)
            .all()
        )
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No documents found for project with id--{project.id}",
            )

        return documents

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrive project documents: {str(e)}",
        )


@router.get("/{project_id}/share")
def share_project(
    project_id: int,
    email: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db)
    # access_type: str = Depends(dependencies.is_owner),
):
    try:
        join_token = invitation_utils.generate_join_token(project_id, email)

        # invitation_utils.save_join_token(email, project_id, join_token)
        db_token = models.ProjectInvitation(
            project_id=project_id,
            join_token=join_token,
            email=email,
        )
        print(db_token, "DODAO SAM")

        db.add(db_token)
        db.commit()

        invitation_utils.send_invitation_email(email, project_id, join_token)

        return {"message": "Invitation sent successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sending invitation failed: {str(e)}",
        )


# It seems that when I click on the link in my Outlook email, the associated function is 
# called three times. Consequently, an exception is triggered due to this repeated invocation
# However, when I manually paste the link from Outlook into the browser, the function 
# is executed only once
# The issue appears to be related to Outlook Cached Mode or Outlook Web Access (OWA).
# The function itself works correctly, but the problem lies in the multiple calls.
# I'm currently unsure how to resolve this.
@router.get("/join")
def join_project(
    project_id: int,
    join_token: str,
    verified: dict = Depends(invitation_utils.verify_join_token),
    db: Session = Depends(get_db),
):
    user_to_invite = (
        db.query(models.User).filter(models.User.email == verified.email).first()
    )

    user_in_table = (
        db.query(models.UserProjectAssociation)
        .filter_by(user_id=user_to_invite.id, project_id=project_id)
        .first()
    )
    print(user_in_table, "Is user in database?")
    if user_in_table is None:
        new_invitation = models.UserProjectAssociation(
            user_id=user_to_invite.id, project_id=project_id
        )

        db.add(new_invitation)
        db.commit()
        db.refresh(new_invitation)
        print("Add in database")
        return {"message": f"Welcome to project"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User are already on that project",
        )


# Maybe we should add owner_id for now because we dont have user
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProjectResponse,
)
def create_project(
    project: dict = Depends(schemas.ProjectCreate),
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # new_project = models.Project(**project.dict())
    new_project = models.Project(owner_id=current_user.id, **project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    logo_url = image_utils.uploading_image_to_s3(logo, new_project.id)

    new_project.logo = logo_url

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
    project: models.Project = Depends(dependencies.get_project),
    file: UploadFile = File(...),
    current_user: dict = Depends(oauth2.get_current_user),
    access_type: str = Depends(dependencies.is_owner_or_participant_off_project),
    db: Session = Depends(get_db),
):
    try:
        if not file_utils.allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX file are allowed",
            )

        s3_url = file_utils.upload_document_to_s3(file, project.id)

        db_document = models.Document(
            project_id=project.id,
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


# We can update just name, description, logo
@router.put("/{id}/info", response_model=schemas.ProjectCreate)
def update_project(
    id: int,
    update_project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    access_type: str = Depends(dependencies.is_owner_or_participant_off_project),
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


# mozda treba model
@router.get("/{id}/logo")
def download_project_logo(
    project: schemas.ProjectBase = Depends(dependencies.get_project),
    current_user: int = Depends(oauth2.get_current_user),
    access_type: str = Depends(dependencies.is_owner_or_participant_off_project),
):
    key = project.logo.split("/")
    filename = key[-1]
    print(filename)
    try:
        key = f"project/{project.id}/{filename}"
        return image_utils.downloading_image_from_s3(key)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download image: {str(e)}"
        )


@router.put("/{id}/logo")
def upserting_project_logo(
    project: schemas.ProjectBase = Depends(dependencies.get_project),
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(None),
    access_type: str = Depends(dependencies.is_owner_or_participant_off_project),
):
    try:
        if file:
            key = project.logo.split("/")
            filename = key[-1]

            existing_image_s3_key = f"project/{project.id}/{filename}"
            new_logo_path = image_utils.update_project_image(
                file=file,
                project_id=project.id,
                existing_image_key=existing_image_s3_key,
            )
            # da li vec postoji takva slika projekta
            # ukoliko ne postoji onda uploaduj novu/izbrisi trenutnu
            print(new_logo_path, "NOVI PATH ZA LOGO")
            project.logo = new_logo_path

            db.commit()
            db.refresh(project)

            return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}",
        )


@router.delete("/{id}/logo")
def delete_project_logo(
    project: models.Project = Depends(dependencies.get_project),
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # ovo mozda i nije potrebno
        if project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this document",
            )
        key = project.logo.split("/")
        filename = key[-1]

        existing_image_s3_key = f"project/{project.id}/{filename}"
        print(existing_image_s3_key, "key za delete")

        image_utils.delete_image_on_s3(existing_image_s3_key)
        project.logo = None

        db.commit()

        return {"message": f"Image with project ID {project.id} has been deleted"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)} ",
        )
