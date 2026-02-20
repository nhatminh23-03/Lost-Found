import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    PORT = int(os.environ.get("PORT", 8000))

    # MongoDB
    MONGODB_URI = os.environ.get("MONGODB_URI", "")
    MONGODB_DB = os.environ.get("MONGODB_DB", "lost_and_found")

    # Cloudflare R2 (S3-compatible)
    R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    R2_ENDPOINT_URL = os.environ.get("R2_ENDPOINT_URL", "")   # https://<acct>.r2.cloudflarestorage.com
    R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "lost-and-found-images")
    R2_PUBLIC_BASE_URL = os.environ.get("R2_PUBLIC_BASE_URL", "")  # https://pub-<hash>.r2.dev

    # Upload constraints
    MAX_IMAGE_BYTES = 5 * 1024 * 1024          # 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024       # Flask hard limit on request body
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
