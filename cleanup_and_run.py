import os
from config import Config
from models import db, User, UserRole
from app import app, seed_users

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted {db_path}")

with app.app_context():
    db.create_all()
    print("Fresh DB created")
    seed_users()
    print("Users seeded")

print("Run: python run_app.py")
print("Access: http://127.0.0.1:5000")
print("Admin login: admin@wvsu.edu.ph / admin123")

