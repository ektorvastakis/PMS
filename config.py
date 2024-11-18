import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SESSION_PERMANENT = True
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite:///parking_slots.db")
    MAX_PARKING_SLOTS = int(os.environ.get('MAX_PARKING_SLOTS', 100))
    BOOKING_ADVANCE_DAYS = int(os.environ.get('BOOKING_ADVANCE_DAYS', 7))
    MIN_BOOKING_DURATION = int(os.environ.get('MIN_BOOKING_DURATION', 30))
    MAX_BOOKING_DURATION = int(os.environ.get('MAX_BOOKING_DURATION', 480))

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    DATABASE_URL = "sqlite:///test.db"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
