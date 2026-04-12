import logging
import os
from config import Config
from models import db, User, UserRole
from app import app, seed_users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)
    logger.info(f"Deleted {db_path}")

with app.app_context():
    db.create_all()
    logger.info("Fresh DB created")
    seed_users()
    logger.info("Users seeded")

print("✓ Ready!")
print("Run: python app.py")
print("URL: http://127.0.0.1:5000")
print("Admin: admin@wvsu.edu.ph / admin123")
print("Alumni login → OTP shows on screen!")
