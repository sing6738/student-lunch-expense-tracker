import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key-in-production")
    
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        import re
        db_url = re.sub(r"\s+", "", db_url)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
    }
    WTF_CSRF_TIME_LIMIT = None
    ITEMS_PER_PAGE = 10
