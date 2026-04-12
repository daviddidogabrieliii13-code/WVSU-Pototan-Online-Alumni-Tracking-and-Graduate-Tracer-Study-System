import os
from config import Config
from models import db, User, UserRole
from app import app, seed_users

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)
    logger.info(f"Deleted {db_path}")

with app.app_context():
    db.create_all()
    logger.info("Fresh DB created")
    seed_users()
    logger.info("Users seeded")

logger.info("Run: python app.py")
logger.info("Access: http://127.0.0.1:5000") 
logger.info("Admin login: admin@wvsu.edu.ph / admin123")

