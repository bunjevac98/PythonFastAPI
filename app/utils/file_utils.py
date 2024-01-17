from app.config import settings
import boto3
from pathlib import Path

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region  # your desired region
BUCKET_NAME = settings.bucket_name  # your desired bucket name
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

    s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}"

    return s3_url


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
