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
AWS_BUCKET_NAME = settings.bucket_name_for_logo
S3_BASE_URL = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def uploading_image_to_s3(file, project_id):
    key = f"project/{project_id}/logo"
    try:
        
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, key)
        return f"{S3_BASE_URL}/{key}"
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not available",
        )
