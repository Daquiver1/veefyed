"""Functions for s3 bucket operations"""

from uuid import UUID

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from src.core.config import (
    ENV,
    S3_ACCESS_KEY_ID,
    S3_BUCKET_NAME,
    S3_REGION,
    S3_SECRET_ACCESS_KEY,
)
from src.utils.formatters import Formatters
from src.utils.helpers import Helpers

s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY_ID,
    aws_secret_access_key=str(S3_SECRET_ACCESS_KEY),
)


class S3Service:
    """Service class for S3 bucket operations."""

    @staticmethod
    def _get_content_type(file_extension: str) -> str:
        """Get content type based on file extension."""
        content_type_map = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        return content_type_map.get(file_extension.lower(), "image/jpeg")

    @staticmethod
    async def upload_restaurant_image_to_bucket(
        image: UploadFile,
        restaurant_id: UUID,
        image_type: str,
    ) -> str:
        """Upload restaurant image to S3 bucket.

        Args:
            image: The image file to upload
            restaurant_id: The restaurant's UUID
            image_type: Type of image - 'logo', 'cover', 'menu_category',
                'menu_item', 'other'

        Returns:
            str: The S3 URL of the uploaded image

        """
        file_extension = image.filename.split(".")[-1].lower()
        file_name = await Helpers.generate_uuid()
        file_path = (
            f"{ENV}/restaurants/{restaurant_id}/images/"
            f"{image_type}/{file_name}.{file_extension}"
        )

        content_type = S3Service._get_content_type(file_extension)

        s3_client.upload_fileobj(
            image.file,
            S3_BUCKET_NAME,
            file_path,
            ExtraArgs={"ContentType": content_type},
        )

        return generate_download_url(key=file_path)


def generate_download_url(*, key: str) -> str:
    """Generate a download url for a file in s3 bucket."""
    return f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}"


def generate_presigned_download_url(*, url: str, expiration: int = 600) -> str:
    """Generate a pre-signed URL to download a file from S3.

    Args:
        key (str): The filename/key of the S3 object.
        is_question (bool, optional): Flag to determine the object path.
            - True: Object is located in the 'past_questions/' directory.
            - False: Object is located in the 'answers/' directory.
            Defaults to False.
        expiration (int, optional): Time in seconds for the pre-signed URL to remain valid.
            Defaults to 60 (1 minute).

    Returns:
        str: A pre-signed URL as a string.

    Raises:
        ClientError: If the pre-signed URL generation fails.

    """
    try:
        object_key = Formatters.extract_object_key_from_url(url)

        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": object_key},
            ExpiresIn=expiration,  # URL validity in seconds
        )
        return presigned_url

    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        raise
