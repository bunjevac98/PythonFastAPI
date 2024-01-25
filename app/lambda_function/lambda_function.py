import os
import tempfile
from PIL import Image
import boto3
from app.config import settings

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
AWS_REGION = settings.aws_region
AWS_BUCKET_NAME = settings.bucket_name_for_logo


def resize_image(image_path, output_path, size=(400, 400)):
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(output_path)


def lambda_handle(event, context):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    # Postavljanje informacija o bucketu i putanji
    source_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    source_key = event["Records"][0]["s3"]["object"]["key"]

    # Privremena datoteka za čuvanje slike nakon promene veličine
    temp_file = tempfile.NamedTemporaryFile()

    # Preuzimanje slike sa S3
    s3.download_file(source_bucket, source_key, temp_file.name)

    # Promena veličine slike
    resized_file_path = "/tmp/resized_" + os.path.basename(source_key)
    resize_image(temp_file.name, resized_file_path)

    project_id = source_key.split("/")[1]
    # Slanje promenjene slike nazad na S3
    target_bucket = AWS_BUCKET_NAME
    target_key = f"project/{project_id}/{temp_file.name}" + os.path.basename(source_key)
    s3.upload_file(resized_file_path, target_bucket, target_key)

    # Opciono: Brisanje privremene datoteke
    temp_file.close()

    return {"statusCode": 200, "body": "Image resized and uploaded to S3."}
