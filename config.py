from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


DB_NAME = "insurance_manager.db"
DB_PATH = BASE_DIR / DB_NAME
DATABASE_URL = f"sqlite:///{DB_PATH}"


DEBUG = True