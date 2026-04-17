import os
import unittest
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
TEST_DB_PATH = ROOT_DIR / "instance" / "test_system_improvements.db"
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
os.environ["MAIL_USERNAME"] = ""
os.environ["MAIL_PASSWORD"] = ""
os.environ["GMAIL_APP_PASSWORD"] = ""

import app as app_module
from models import AlumniProfile, EmailVerificationToken, PasswordReset, User, UserRole


class SystemImprovementsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app_module.app
        self.client = self.app.test_client()
        self.photo_path = ROOT_DIR / "static" / "uploads" / "profile_photos" / "test-cleanup-photo.jpg"
        self.photo_path.parent.mkdir(parents=True, exist_ok=True)

        with self.app.app_context():
            app_module.db.session.remove()
            app_module.db.drop_all()
            app_module.db.create_all()
            self._seed_users()

    def tearDown(self):
        if self.photo_path.exists():
            self.photo_path.unlink()
        with self.app.app_context():
            app_module.db.session.remove()
            app_module.db.drop_all()
            app_module.db.engine.dispose()
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()

    def _seed_users(self):
        self.photo_path.write_bytes(b"\xff\xd8\xff\xe0cleanup-test")

        admin = User(
            email="admin@wvsu.edu.ph",
            role=UserRole.ADMIN,
            otp_verified=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            is_active=True,
            approval_status="approved",
            approval_requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
        )
        admin.set_password("Admin123!")

        alumni = User(
            email="alumni@example.com",
            role=UserRole.ALUMNI,
            otp_verified=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            is_active=True,
            approval_status="approved",
            approval_requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
        )
        alumni.set_password("Alumni123!")

        app_module.db.session.add_all([admin, alumni])
        app_module.db.session.flush()

        profile = AlumniProfile(
            user_id=alumni.id,
            first_name="Test",
            last_name="Alumni",
            degree="Bachelor of Science in Information Technology (BSIT)",
            year_graduated=2024,
            profile_photo="uploads/profile_photos/test-cleanup-photo.jpg",
            profile_completed=True,
        )
        app_module.db.session.add(profile)
        app_module.db.session.flush()

        app_module.db.session.add(
            PasswordReset(
                user_id=alumni.id,
                token="reset-token",
                used=False,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
        )
        app_module.db.session.add(
            EmailVerificationToken(
                user_id=alumni.id,
                token="verify-token",
                used=False,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )
        )
        app_module.db.session.commit()

        self.admin_id = admin.id
        self.alumni_id = alumni.id

    def _login_as(self, user_id):
        with self.client.session_transaction() as session:
            session["_user_id"] = str(user_id)
            session["_fresh"] = True

    def test_bulk_delete_removes_user_dependencies_and_profile_photo(self):
        self._login_as(self.admin_id)

        response = self.client.post(
            "/admin/users/bulk-delete",
            data={"selected_ids": [str(self.alumni_id)]},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully deleted 1 alumni accounts.", response.data)
        self.assertFalse(self.photo_path.exists())

        with self.app.app_context():
            self.assertIsNone(app_module.db.session.get(User, self.alumni_id))
            self.assertEqual(
                PasswordReset.query.filter_by(user_id=self.alumni_id).count(),
                0,
            )
            self.assertEqual(
                EmailVerificationToken.query.filter_by(user_id=self.alumni_id).count(),
                0,
            )

    def test_system_reset_clears_tokens_records_and_uploaded_profile_photos(self):
        self._login_as(self.admin_id)

        response = self.client.post(
            "/admin/system-reset",
            data={"confirmation_phrase": "RESET SYSTEM", "keep_default_admin": "1"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"System reset complete. Default admin account was retained.", response.data)
        self.assertFalse(self.photo_path.exists())

        with self.app.app_context():
            self.assertIsNotNone(
                User.query.filter_by(email="admin@wvsu.edu.ph").first()
            )
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(AlumniProfile.query.count(), 0)
            self.assertEqual(PasswordReset.query.count(), 0)
            self.assertEqual(EmailVerificationToken.query.count(), 0)

    def test_missing_smtp_credentials_use_mock_delivery(self):
        self.assertTrue(app_module.should_mock_email_delivery())


if __name__ == "__main__":
    unittest.main()
