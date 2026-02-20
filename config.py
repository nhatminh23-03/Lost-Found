import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

    MONGODB_URI = os.environ.get("MONGODB_URI")
    MONGODB_DB = os.environ.get("MONGODB_DB", "lost_and_found")

    R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
    R2_ENDPOINT_URL = os.environ.get("R2_ENDPOINT_URL")
    R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
    R2_PUBLIC_BASE_URL = os.environ.get("R2_PUBLIC_BASE_URL", "")

    PORT = int(os.environ.get("PORT", 5000))
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")

    # Flask hard limit on incoming request body (image + form fields)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
