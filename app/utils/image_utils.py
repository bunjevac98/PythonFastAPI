from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from app.config import settings
import boto3
from botocore.exceptions import NoCredentialsError
from PIL import Image
import io
import os
import tempfile


AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region
AWS_BUCKET_NAME = settings.bucket_name_for_logo
S3_BASE_URL = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)



def uploading_image_to_s3(file, project_id):
    key = f"project/{project_id}/{file.filename}"
    try:
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, key)
        return f"{S3_BASE_URL}/{key}"
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )


def downloading_image_from_s3(key: str):
    try:
        response = s3_client.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
        content_type = response["ContentType"]
        print(content_type, "OVO JE KEY")
        streaming_body = response["Body"]

        return StreamingResponse(
            streaming_body,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={key}"},
        )
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )


def update_project_image(file, project_id, existing_image_key):
    try:
        s3_key = f"project/{project_id}/{file.filename}"

        if s3_key == existing_image_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="We already have image with key: {existing_file_key}",
            )

        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, s3_key)
        print(s3_key, "Novi key")
        if existing_image_key:
            s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=existing_image_key)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AWS credentials not available, we didnt delete object with key{existing_file_key}",
            )
        return f"{S3_BASE_URL}/{s3_key}"

    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )


def delete_image_on_s3(path_key):
    try:
        if path_key:
            s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=path_key)
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )
