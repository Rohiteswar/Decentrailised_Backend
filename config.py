
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    default_sqlite_path = "sqlite:///notes.db"
    if os.getenv("RENDER") == "true":
        default_sqlite_path = "sqlite:////tmp/notes.db"

    RAW_DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_path)

    SQLALCHEMY_DATABASE_URI = RAW_DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")