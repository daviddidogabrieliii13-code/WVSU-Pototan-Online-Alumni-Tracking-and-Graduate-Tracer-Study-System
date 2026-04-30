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
from models import (
    AlumniProfile,
    EmailVerificationToken,
    Event,
    Notification,
    PasswordReset,
    User,
    UserRole,
)


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

        director = User(
            email="director@wvsu.edu.ph",
            role=UserRole.DIRECTOR,
            otp_verified=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            is_active=True,
            approval_status="approved",
            approval_requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
        )
        director.set_password("Director123!")

        registrar = User(
            email="registrar@wvsu.edu.ph",
            role=UserRole.REGISTRAR,
            otp_verified=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            is_active=True,
            approval_status="approved",
            approval_requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
        )
        registrar.set_password("Registrar123!")

        osa = User(
            email="osa@wvsu.edu.ph",
            role=UserRole.OSA,
            otp_verified=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            is_active=True,
            approval_status="approved",
            approval_requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
        )
        osa.set_password("Osa12345!")

        app_module.db.session.add_all([admin, alumni, director, registrar, osa])
        app_module.db.session.flush()

        profile = AlumniProfile(
            user_id=alumni.id,
            first_name="Test",
            last_name="Alumni",
            student_id="2024-0001",
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
        self.director_id = director.id
        self.registrar_id = registrar.id
        self.osa_id = osa.id

    def _login_as(self, user_id):
        with self.app.app_context():
            user = app_module.db.session.get(User, user_id)
            role_slug = app_module.to_role_slug(user.role, default="alumni")

        with self.client.session_transaction() as session:
            session["_user_id"] = str(user_id)
            session["_fresh"] = True
            session[app_module.ACTIVE_USER_ID_KEY] = user_id
            session[app_module.ACTIVE_ROLE_KEY] = role_slug
            session.pop(app_module.AUTH_TOKEN_SESSION_KEY, None)
            session.pop(app_module.AUTH_TOKEN_EXPIRY_SESSION_KEY, None)
            session.pop(app_module.OTP_SESSION_KEY, None)

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

    def test_missing_smtp_credentials_keep_otp_ui_fallback(self):
        original_show_otp = self.app.config.get("SHOW_OTP_IN_UI")
        self.app.config["SHOW_OTP_IN_UI"] = True
        try:
            delivery_mode = app_module.send_otp(
                "external.user@example.com",
                "123456",
                role_slug="alumni",
            )
        finally:
            self.app.config["SHOW_OTP_IN_UI"] = original_show_otp

        self.assertEqual(delivery_mode, "ui")

    def test_security_headers_are_applied(self):
        response = self.client.get("/")

        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(
            response.headers.get("Referrer-Policy"),
            "strict-origin-when-cross-origin",
        )

    def test_job_creation_dispatches_notifications_to_all_roles(self):
        self._login_as(self.admin_id)

        response = self.client.post(
            "/admin/jobs/add",
            data={
                "title": "Backend Developer",
                "company": "WVSU Tech Hub",
                "location": "Iloilo",
                "job_type": "full-time",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Job created.", response.data)

        with self.app.app_context():
            notifications = Notification.query.order_by(Notification.user_id.asc()).all()
            self.assertEqual(len(notifications), 5)
            self.assertEqual({item.source_role for item in notifications}, {"admin"})
            self.assertEqual({item.notification_type for item in notifications}, {"job"})
            self.assertEqual(
                {item.user.role.value for item in notifications},
                {"admin", "alumni", "director", "registrar", "osa"},
            )

    def test_api_event_update_dispatches_notifications_to_all_roles(self):
        with self.app.app_context():
            event = Event(
                title="Alumni Homecoming",
                event_date=datetime.utcnow() + timedelta(days=14),
                location="Pototan",
                is_published=True,
            )
            app_module.db.session.add(event)
            app_module.db.session.commit()
            event_id = event.id

        self._login_as(self.admin_id)
        response = self.client.put(
            f"/api/v1/events/{event_id}",
            json={
                "title": "Alumni Homecoming 2026",
                "event_date": (datetime.utcnow() + timedelta(days=21)).strftime("%Y-%m-%dT%H:%M"),
                "location": "Pototan Campus Gymnasium",
                "is_published": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["notification_dispatch"]["created"], 5)

        with self.app.app_context():
            notifications = Notification.query.order_by(Notification.user_id.asc()).all()
            self.assertEqual(len(notifications), 5)
            self.assertEqual({item.source_role for item in notifications}, {"admin"})
            self.assertEqual({item.notification_type for item in notifications}, {"event"})
            self.assertIn("updated", notifications[0].title.lower())

    def test_admin_navigation_renders_shared_notification_and_export_links(self):
        self._login_as(self.admin_id)

        response = self.client.get("/admin/password-management")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Notifications", response.data)
        self.assertIn(b"Data Exports", response.data)
        self.assertIn(b'data-portal-role="admin"', response.data)

    def test_privileged_pages_render_matching_portal_shells(self):
        pages = [
            (self.admin_id, "/admin/password-management", b'data-portal-role="admin"'),
            (self.registrar_id, "/admin/alumni", b'data-portal-role="registrar"'),
            (self.director_id, "/analytics", b'data-portal-role="director"'),
            (self.osa_id, "/admin/events", b'data-portal-role="osa"'),
        ]

        for user_id, path, expected_shell in pages:
            self._login_as(user_id)
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn(expected_shell, response.data)

    def test_admin_dashboard_password_card_uses_real_reset_route(self):
        self._login_as(self.admin_id)

        response = self.client.get("/portal/admin/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/reset-password", response.data)
        self.assertNotIn(b"openChangePasswordModal", response.data)

    def test_admin_alumni_search_matches_student_id(self):
        self._login_as(self.admin_id)

        response = self.client.get("/admin/alumni?search=2024-0001")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test", response.data)


if __name__ == "__main__":
    unittest.main()
