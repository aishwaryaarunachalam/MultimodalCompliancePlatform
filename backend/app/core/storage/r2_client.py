import io
from typing import Optional
import boto3
from botocore.config import Config
from app.config import settings


class R2Client:
    """Thin boto3 wrapper for Cloudflare R2 / any S3-compatible storage."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL or f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        return self._client

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload raw bytes; returns the object key."""
        self._get_client().put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def upload_fileobj(self, key: str, fileobj, content_type: str = "application/octet-stream") -> str:
        """Upload a file-like object (streaming)."""
        self._get_client().upload_fileobj(
            fileobj,
            settings.R2_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    def download_bytes(self, key: str) -> bytes:
        """Download an object and return raw bytes."""
        response = self._get_client().get_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        return response["Body"].read()

    def get_presigned_url(self, key: str, expires: int = 3600) -> str:
        """Generate a presigned GET URL (valid for `expires` seconds)."""
        return self._get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET_NAME, "Key": key},
            ExpiresIn=expires,
        )

    def delete_object(self, key: str) -> None:
        self._get_client().delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)

    def public_url(self, key: str) -> Optional[str]:
        """Return a public URL if the bucket has public access configured."""
        if settings.R2_PUBLIC_URL:
            return f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
        return None


# Module-level singleton
r2 = R2Client()
