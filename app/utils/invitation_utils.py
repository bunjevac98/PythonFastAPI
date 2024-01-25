import secrets
from fastapi import Depends, HTTPException, status
import boto3
from app.config import settings
import hashlib
from app.schemas import ProjectInvitationCreate
from database.database import get_db
from sqlalchemy.orm import Session
from database import models

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region
SNS_TOPIC_ARN = settings.sns_topic_arn

sns_client = boto3.client(
    "sns",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def send_invitation_email(email, project_id, join_token):
    try:
        subject = f"Join project {project_id}"
        message = f"Click here to join: http://localhost:8000/projects/join?project_id={project_id}&join_token={join_token}"

        sns_response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageStructure="string",
        )

        sns_response.get("MessageId")

        # Subscribe the email address to the SNS topic
        subscribe_response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email,
        )
        print(subscribe_response)
    except Exception as e:
        print(
            f"Error sending invitation email to {email} for project {project_id}: {str(e)}"
        )



def generate_join_token(project_id, email):
    combined_string = f"{project_id}-{email}"
    hashed_imput = hashlib.sha256(combined_string.encode()).hexdigest()
    token = f"{hashed_imput}_{secrets.token_urlsafe(16)}"
    return token


def save_join_token(
    email: str, project_id: int, join_token: str, db: Session = Depends(get_db)
):
    """
    print(invitation_data, "Invitation data")
    db_token = ProjectInvitationCreate(**invitation_data.model_dump())
    """
    print("Usao da saucam token")
    print(project_id)
    db_token = ProjectInvitationCreate(
        project_id=project_id,
        join_token=join_token,
        email=email,
    )

    db.add(db_token)
    db.commit()

    return


# email
def verify_join_token(project_id: int, join_token: str, db: Session = Depends(get_db)):
    verified = (
        db.query(models.ProjectInvitation)
        .filter(
            models.ProjectInvitation.project_id == project_id,
            models.ProjectInvitation.join_token == join_token,
        )
        .first()
    )
    if verified is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, details="Invalid join token"
        )
    return verified
