from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from app import schemas
from app.config import settings
import boto3
from pathlib import Path
from botocore.exceptions import NoCredentialsError

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region
BUCKET_NAME = settings.bucket_name
ALLOWED_EXTENSIONS = {"pdf", "docx"}


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def validate_file_extension(file_name: str, allowed_extensions: set):
    ext = Path(file_name).suffix.lower()[1:]
    return ext in allowed_extensions


def upload_document_to_s3(file, project_id):
    # generating unique file key
    file_key = f"{project_id}/{file.filename}"

    s3_client.upload_fileobj(file.file, BUCKET_NAME, file_key)

    s3_url = file_key

    return s3_url


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_document_file_path(document: schemas.Document) -> str:
    #  path to my document files
    return document.file_path


def download_document_from_s3(document: schemas.Document, file_key: str):
    try:
        # Generate a presigned URL for temporary access to the file

        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        content_type = response["ContentType"]
        streaming_body = response["Body"]

        return StreamingResponse(
            streaming_body,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_key}"},
        )
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )


def update_document_on_s3(file, project_id, existing_file_key):
    try:
        s3_key = f"{project_id}/{file.filename}"
        s3_client.upload_fileobj(file.file, BUCKET_NAME, s3_key)
        print(s3_key, "Novi key")

        if existing_file_key:
            print(existing_file_key, "Stari key")
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=existing_file_key)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials not available, we didnt delete object with key{existing_file_key}",
            )
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )


def delete_document_on_s3(path_key):
    try:
        if path_key:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=path_key)

    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )
