from __future__ import annotations

import uuid
from typing import BinaryIO

import boto3
from botocore.config import Config as BotoConfig
from flask import current_app


def _get_s3_client():
    """Build a boto3 S3 client configured for Cloudflare R2."""
    cfg = current_app.config
    return boto3.client(
        "s3",
        endpoint_url=cfg["R2_ENDPOINT_URL"],
        aws_access_key_id=cfg["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=cfg["R2_SECRET_ACCESS_KEY"],
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def upload_image(file_obj: BinaryIO, original_filename: str) -> str:
    """Upload *file_obj* to R2 and return the public URL.

    Object key format: posts/<uuid>.<ext>
    """
    cfg = current_app.config
    ext = original_filename.rsplit(".", 1)[-1].lower()
    object_key = f"posts/{uuid.uuid4()}.{ext}"

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        cfg["R2_BUCKET_NAME"],
        object_key,
        ExtraArgs={"ContentType": _content_type(ext)},
    )

    public_base = cfg.get("R2_PUBLIC_BASE_URL") or ""
    public_base = public_base.rstrip("/") if public_base else ""

    # If a public base URL is configured and looks like a public origin, use it.
    if public_base and public_base.startswith("http"):
        return f"{public_base}/{object_key}"

    # Otherwise return a presigned GET URL (short-lived) so the app can display the image
    # even when the bucket/public origin isn't configured yet.
    try:
        presigned = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": cfg["R2_BUCKET_NAME"], "Key": object_key},
            ExpiresIn=3600,
        )
        return presigned
    except Exception:
        # Last resort: return the object key (not a full URL) so callers can detect failure.
        return object_key


def _content_type(ext: str) -> str:
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(ext, "application/octet-stream")
