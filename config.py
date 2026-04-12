import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wvsu-alumni-tracer-2024-secure-key'
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
    SHOW_OTP_IN_UI = os.environ.get('SHOW_OTP_IN_UI', 'False').lower() in ['true', 'on', '1']

    # RSVP access settings
    RSVP_ALLOWED_ROLES = os.environ.get('RSVP_ALLOWED_ROLES') or 'alumni'
    
    # Background Image Settings
    # Set to True to use a custom background image
    USE_CUSTOM_BACKGROUND = os.environ.get('USE_CUSTOM_BACKGROUND') or True
    # Path to custom background image (relative to static folder)
    CUSTOM_BACKGROUND = os.environ.get('CUSTOM_BACKGROUND') or 'C:/Users/ellaa/Downloads/gabo.jpg'
    # Background opacity (0.0 to 1.0)
    BACKGROUND_OPACITY = 0.15
    
    # Email Settings (Gmail App Password supported)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'daviddidogabrieliii13@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or os.environ.get('GMAIL_APP_PASSWORD') or 'cfkxgjxmkaznrqaz'
    MAIL_FROM = os.environ.get('MAIL_FROM') or MAIL_USERNAME
    
    # Admin emails
    ADMIN_EMAILS = ['admin@wvsu.edu.ph']
    REGISTRAR_EMAIL = 'registrar@wvsu.edu.ph'
    OSA_EMAIL = 'osa@wvsu.edu.ph'
    DIRECTOR_EMAIL = 'director@wvsu.edu.ph'
