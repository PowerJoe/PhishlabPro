import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data', 'phishing.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    EVILGINX_PATH = os.path.join(basedir, 'evilginx2')
    EVILGINX_DOMAIN = os.environ.get('EVILGINX_DOMAIN') or 'phish.sentinelsec.nl'
    UPLOAD_FOLDER = os.path.join(basedir, 'data', 'uploads')
    CAPTURES_FOLDER = os.path.join(basedir, 'data', 'captures')
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    APP_NAME = "PhishLab Pro"
    APP_VERSION = "1.0.0"

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
