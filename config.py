import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wvsu-alumni-tracer-2024-secure-key'

    # ✅ FIXED: Render-safe SQLite path
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "database.db")
    )

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
    SHOW_OTP_IN_UI = True

    # RSVP access settings
    RSVP_ALLOWED_ROLES = os.environ.get('RSVP_ALLOWED_ROLES') or 'alumni'

    # Background Image Settings
    USE_CUSTOM_BACKGROUND = os.environ.get('USE_CUSTOM_BACKGROUND') or True
    CUSTOM_BACKGROUND = os.environ.get('CUSTOM_BACKGROUND') or 'static/uploads/background.jpg'
    BACKGROUND_OPACITY = 0.15

    # Email Settings (SECURE FIX)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM = os.environ.get('MAIL_FROM') or MAIL_USERNAME

    # OTP: ON-SCREEN + Gmail
    EMAIL_VERIFICATION_REQUIRED = False
    SHOW_OTP_IN_UI = True
    EMAIL_NOTIFICATION_ENABLED = True

    # Admin emails
    ADMIN_EMAILS = ['admin@wvsu.edu.ph']
    REGISTRAR_EMAIL = 'registrar@wvsu.edu.ph'
    OSA_EMAIL = 'osa@wvsu.edu.ph'
    DIRECTOR_EMAIL = 'director@wvsu.edu.ph'