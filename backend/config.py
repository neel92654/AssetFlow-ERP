import os
import urllib.parse
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key')
    
    # SQLAlchemy
    DB_USERNAME = os.environ.get('DB_USERNAME', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'assetflow')
    
    import urllib.parse
    DB_PASSWORD_ENCODED = urllib.parse.quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Config
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # File Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(basedir, 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_SIZE', 10 * 1024 * 1024)) # 10MB
    
    # Logging
    LOG_DIR = os.path.join(basedir, 'logs')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DB_PASSWORD_ENCODED = urllib.parse.quote_plus(os.environ.get('DB_PASSWORD', 'root'))
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USERNAME', 'root')}:{DB_PASSWORD_ENCODED}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '3306')}/assetflow_test"

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
