import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Safe local/dev fallback only. Set SECRET_KEY in the environment for deployed use.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Pagination
    ITEMS_PER_PAGE = 10
    
    # Survey settings
    SURVEY_REQUIRED_FIELDS = [
        'education_quality',
        'curriculum_relevance',
        'facilities_rating',
        'competency_technical',
        'competency_soft',
        'competency_problem',
        'overall_satisfaction',
        'recommend_rating'
    ]

    # OTP security settings
    OTP_EXPIRY_SECONDS = int(os.environ.get('OTP_EXPIRY_SECONDS') or 300)
    OTP_MAX_ATTEMPTS = int(os.environ.get('OTP_MAX_ATTEMPTS') or 5)
    OTP_RESEND_COOLDOWN_SECONDS = int(os.environ.get('OTP_RESEND_COOLDOWN_SECONDS') or 45)
    OTP_LOCKOUT_SECONDS = int(os.environ.get('OTP_LOCKOUT_SECONDS') or 300)
    OTP_REQUEST_RATE_LIMIT_MAX = int(os.environ.get('OTP_REQUEST_RATE_LIMIT_MAX') or 3)
    OTP_REQUEST_RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get('OTP_REQUEST_RATE_LIMIT_WINDOW_SECONDS') or 60)
    OTP_VERIFY_RATE_LIMIT_MAX = int(os.environ.get('OTP_VERIFY_RATE_LIMIT_MAX') or 8)
    OTP_VERIFY_RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get('OTP_VERIFY_RATE_LIMIT_WINDOW_SECONDS') or 300)
    SHOW_OTP_IN_UI = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_EXPIRY_DAYS = int(os.environ.get('JWT_EXPIRY_DAYS') or 7)
    AUTH_TOKEN_COOKIE_NAME = os.environ.get('AUTH_TOKEN_COOKIE_NAME') or 'wvsu_auth_token'

    # RSVP access settings
    RSVP_ALLOWED_ROLES = os.environ.get('RSVP_ALLOWED_ROLES') or 'alumni'
    
    # Background Image Settings
    USE_CUSTOM_BACKGROUND = os.environ.get('USE_CUSTOM_BACKGROUND', 'False').lower() in ['true', 'on', '1']
    CUSTOM_BACKGROUND = os.environ.get('CUSTOM_BACKGROUND') or ''
    try:
        BACKGROUND_OPACITY = float(os.environ.get('BACKGROUND_OPACITY') or 0.15)
    except (TypeError, ValueError):
        BACKGROUND_OPACITY = 0.15
    
    # Email Settings (Gmail App Password supported)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'daviddidogabrieliii13@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or os.environ.get('GMAIL_APP_PASSWORD') or 'fsfsevfttqyjsntf'
    MAIL_FROM = os.environ.get('MAIL_FROM') or MAIL_USERNAME or 'no-reply@wvsu.local'
    
    # OTP: ON-SCREEN + Gmail (Render ready)
    EMAIL_VERIFICATION_REQUIRED = False
    EMAIL_NOTIFICATION_ENABLED = True
    
    # Admin emails
    ADMIN_EMAILS = ['admin@wvsu.edu.ph']
    REGISTRAR_EMAIL = 'registrar@wvsu.edu.ph'
    OSA_EMAIL = 'osa@wvsu.edu.ph'
    DIRECTOR_EMAIL = 'director@wvsu.edu.ph'
