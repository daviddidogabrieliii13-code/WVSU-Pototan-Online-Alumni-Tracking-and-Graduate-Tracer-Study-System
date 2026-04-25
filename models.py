import enum
import hashlib
import hmac
from datetime import datetime

import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


def _iso(value):
    return value.isoformat() if value else None


def _role_value(role):
    if isinstance(role, UserRole):
        return role.value
    if role is None:
        return "alumni"
    text = str(role).strip()
    if text.startswith("UserRole."):
        text = text.split(".", 1)[1]
    return text.lower()


class UserRole(enum.Enum):
    ALUMNI = "alumni"
    ADMIN = "admin"
    DIRECTOR = "director"
    REGISTRAR = "registrar"
    OSA = "osa"


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.ALUMNI, nullable=False)
    otp_code_hash = db.Column(db.String(256))
    otp_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=True, nullable=False)
    email_verified_at = db.Column(db.DateTime)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    temporary_password_issued_at = db.Column(db.DateTime)
    approval_status = db.Column(db.String(20), default="approved", nullable=False)
    approval_requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    approved_at = db.Column(db.DateTime)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    approval_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    profile = db.relationship("AlumniProfile", backref="user", uselist=False)
    logs = db.relationship("SystemLog", backref="user", cascade="all, delete-orphan")
    notifications = db.relationship(
        "Notification", backref="user", cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_otp(self, otp):
        otp_bytes = (otp or "").encode("utf-8")
        self.otp_code_hash = bcrypt.hashpw(otp_bytes, bcrypt.gensalt()).decode("utf-8")

    def verify_otp(self, otp):
        if not otp or not self.otp_code_hash:
            return False
        stored_hash = str(self.otp_code_hash)
        otp_bytes = otp.encode("utf-8")

        if stored_hash.startswith("$2"):
            try:
                return bcrypt.checkpw(otp_bytes, stored_hash.encode("utf-8"))
            except ValueError:
                return False

        provided_hash = hashlib.sha256(otp_bytes).hexdigest()
        return hmac.compare_digest(provided_hash, stored_hash)

    def to_dict(self, include_profile=False):
        payload = {
            "id": self.id,
            "email": self.email,
            "role": _role_value(self.role),
            "otp_verified": bool(self.otp_verified),
            "is_active": bool(self.is_active),
            "email_verified": bool(self.email_verified),
            "email_verified_at": _iso(self.email_verified_at),
            "must_change_password": bool(self.must_change_password),
            "temporary_password_issued_at": _iso(self.temporary_password_issued_at),
            "approval_status": self.approval_status,
            "approval_requested_at": _iso(self.approval_requested_at),
            "approved_at": _iso(self.approved_at),
            "approved_by_user_id": self.approved_by_user_id,
            "approval_notes": self.approval_notes,
            "created_at": _iso(self.created_at),
            "last_login": _iso(self.last_login),
        }
        if include_profile:
            payload["profile"] = self.profile.to_dict() if self.profile else None
        return payload


class AlumniProfile(db.Model):
    __tablename__ = "alumni_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    civil_status = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    province = db.Column(db.String(100))
    facebook_link = db.Column(db.String(500))
    linkedin_link = db.Column(db.String(500))

    student_id = db.Column(db.String(50), unique=True)
    degree = db.Column(db.String(200), nullable=False)
    year_graduated = db.Column(db.Integer)
    honors = db.Column(db.Text)
    activities = db.Column(db.Text)

    father_name = db.Column(db.String(120))
    father_contact = db.Column(db.String(30))
    mother_name = db.Column(db.String(120))
    mother_contact = db.Column(db.String(30))
    guardian_name = db.Column(db.String(120))
    guardian_contact = db.Column(db.String(30))

    enrollment_status = db.Column(db.String(100))
    enrolled_program = db.Column(db.String(200))
    enrollment_date = db.Column(db.Date)
    expected_completion_date = db.Column(db.Date)

    employment_status = db.Column(db.String(50), default="student")
    current_employer = db.Column(db.String(200))
    job_position = db.Column(db.String(200))
    employment_duration = db.Column(db.String(50))
    salary_range = db.Column(db.String(100))
    work_location = db.Column(db.String(200))
    job_description = db.Column(db.Text)

    skills = db.Column(db.Text)
    certifications = db.Column(db.Text)
    volunteer_work = db.Column(db.Text)

    profile_photo = db.Column(db.String(500))
    profile_completed = db.Column(db.Boolean, default=False)
    survey_completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    surveys = db.relationship(
        "TracerSurvey", backref="alumni_profile", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "civil_status": self.civil_status,
            "gender": self.gender,
            "date_of_birth": _iso(self.date_of_birth),
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "province": self.province,
            "facebook_link": self.facebook_link,
            "linkedin_link": self.linkedin_link,
            "student_id": self.student_id,
            "degree": self.degree,
            "year_graduated": self.year_graduated,
            "honors": self.honors,
            "activities": self.activities,
            "employment_status": self.employment_status,
            "current_employer": self.current_employer,
            "job_position": self.job_position,
            "employment_duration": self.employment_duration,
            "salary_range": self.salary_range,
            "work_location": self.work_location,
            "job_description": self.job_description,
            "skills": self.skills,
            "certifications": self.certifications,
            "volunteer_work": self.volunteer_work,
            "profile_photo": self.profile_photo,
            "profile_completed": bool(self.profile_completed),
            "survey_completed": bool(self.survey_completed),
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }


class TracerSurvey(db.Model):
    __tablename__ = "survey_response"

    id = db.Column(db.Integer, primary_key=True)
    alumni_id = db.Column(db.Integer, db.ForeignKey("alumni_profile.id"), nullable=False)

    education_quality = db.Column(db.Integer)
    curriculum_relevance = db.Column(db.Integer)
    facilities_rating = db.Column(db.Integer)
    instructor_quality = db.Column(db.Integer)
    research_opportunities = db.Column(db.Integer)

    competency_technical = db.Column(db.Integer)
    competency_soft = db.Column(db.Integer)
    competency_problem = db.Column(db.Integer)
    competency_communication = db.Column(db.Integer)
    competency_leadership = db.Column(db.Integer)

    is_employed = db.Column(db.Boolean)
    job_related = db.Column(db.Boolean)
    job_searching = db.Column(db.Boolean)
    employment_sector = db.Column(db.String(100))

    overall_satisfaction = db.Column(db.Integer)
    recommend_rating = db.Column(db.Integer)
    suggestions = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Job(db.Model):
    __tablename__ = "job"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(200))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    job_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index("ix_job_active_posted", "is_active", "posted_date"),)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "requirements": self.requirements,
            "location": self.location,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "job_type": self.job_type,
            "category": self.category,
            "is_active": bool(self.is_active),
            "posted_date": _iso(self.posted_date),
        }


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(100))
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    organizer = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    is_published = db.Column(db.Boolean, default=False)

    __table_args__ = (db.Index("ix_event_date_published", "event_date", "is_published"),)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type,
            "event_date": _iso(self.event_date),
            "location": self.location,
            "venue": self.venue,
            "organizer": self.organizer,
            "contact_email": self.contact_email,
            "is_published": bool(self.is_published),
        }


class EventRSVP(db.Model):
    __tablename__ = "rsvps"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = db.relationship(
        "Event",
        backref=db.backref("rsvps", lazy="dynamic", cascade="all, delete-orphan"),
    )
    user = db.relationship(
        "User",
        backref=db.backref("event_rsvps", lazy="dynamic", cascade="all, delete-orphan"),
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", name="uq_rsvps_user_event"),
        db.Index("ix_rsvps_status", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "status": self.status,
            "timestamp": _iso(self.timestamp),
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }


class PasswordReset(db.Model):
    __tablename__ = "password_reset"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    token = db.Column(db.String(500), nullable=False, index=True)
    used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailVerificationToken(db.Model):
    __tablename__ = "email_verification_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SystemLog(db.Model):
    __tablename__ = "system_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45))
    device = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True)
    generated_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    report_type = db.Column(db.String(50))
    parameters = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500))


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    notification_type = db.Column(db.String(50))
    source_role = db.Column(db.String(50), nullable=False, default="system")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "source_role": self.source_role,
            "is_read": bool(self.is_read),
            "created_at": _iso(self.created_at),
        }
