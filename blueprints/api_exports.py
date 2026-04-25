import csv
import io
import re
from datetime import datetime
from functools import wraps
from types import SimpleNamespace

from flask import Blueprint, Response, jsonify, request
from flask_login import current_user

from models import Event, Job, Notification, User, UserRole, db


api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
export_bp = Blueprint("exports", __name__, url_prefix="/exports")

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def _clean_text(value):
    return (value or "").strip()


def _role_slug(value):
    if value is None:
        return "alumni"
    if isinstance(value, UserRole):
        return value.value
    text = str(value).strip()
    if text.startswith("UserRole."):
        text = text.split(".", 1)[1]
    return text.lower()


def _json_error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def _current_role():
    if not current_user.is_authenticated:
        return None
    return _role_slug(getattr(current_user, "role", None))


def _api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return _json_error("Authentication required.", 401)
        return view(*args, **kwargs)

    return wrapped


def _roles_required(*roles):
    allowed = {str(role).lower() for role in roles}

    def decorator(view):
        @wraps(view)
        @_api_login_required
        def wrapped(*args, **kwargs):
            if _current_role() not in allowed:
                return _json_error("You do not have permission for this action.", 403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def _load_json_payload():
    if not request.is_json:
        return None, _json_error("JSON body is required.", 415)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, _json_error("Malformed JSON body.", 400)
    return payload, None


def _parse_bool(value, default=False):
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_datetime(value):
    text = _clean_text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed
        except ValueError:
            continue
    return None


def _parse_optional_int(value, field_name):
    if value is None:
        return None, None
    if isinstance(value, int):
        return value, None
    text = _clean_text(str(value))
    if not text:
        return None, None
    try:
        return int(text), None
    except (TypeError, ValueError):
        return None, f"{field_name} must be a valid integer."


def _paginate(query, default_per_page=20, max_per_page=100):
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    per_page = min(max(1, per_page), max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def _safe_commit(message="Unable to save changes right now."):
    try:
        db.session.commit()
        return None
    except Exception:
        db.session.rollback()
        return _json_error(message, 500)


def _role_enum(value):
    role_slug = _role_slug(value)
    if role_slug not in {"alumni", "admin", "director", "registrar", "osa"}:
        return None
    return UserRole[role_slug.upper()]


def _valid_email(value):
    return bool(EMAIL_PATTERN.fullmatch(_clean_text(value)))


def _csv_response(filename, headers, rows):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    payload = stream.getvalue()
    stream.close()
    return Response(
        payload,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@api_bp.route("/users", methods=["GET"])
@_roles_required("admin")
def api_users_list():
    query = User.query.order_by(User.id.desc())
    pagination = _paginate(query)
    return (
        jsonify(
            {
                "success": True,
                "data": [user.to_dict(include_profile=True) for user in pagination.items],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@api_bp.route("/users", methods=["POST"])
@_roles_required("admin")
def api_users_create():
    payload, error = _load_json_payload()
    if error:
        return error

    email = _clean_text(payload.get("email")).lower()
    password = payload.get("password") or ""
    role_enum = _role_enum(payload.get("role") or "alumni")
    if not email or not password:
        return _json_error("Both email and password are required.", 400)
    if not _valid_email(email):
        return _json_error("Invalid email format.", 400)
    if role_enum is None:
        return _json_error("Invalid role. Allowed: alumni, admin, director, registrar, osa.", 400)
    if User.query.filter_by(email=email).first():
        return _json_error("Email already exists.", 409)

    user = User(email=email, role=role_enum)
    user.set_password(password)
    user.otp_verified = _parse_bool(payload.get("otp_verified"), default=False)
    user.email_verified = _parse_bool(payload.get("email_verified"), default=True)
    user.email_verified_at = datetime.utcnow() if user.email_verified else None
    user.is_active = _parse_bool(payload.get("is_active"), default=False)
    approval_status = (_clean_text(payload.get("approval_status")) or "approved").lower()
    if approval_status not in {"pending", "approved", "rejected"}:
        return _json_error("approval_status must be pending, approved, or rejected.", 400)
    user.approval_status = approval_status
    user.approval_requested_at = datetime.utcnow()
    if user.approval_status == "approved":
        user.approved_at = datetime.utcnow()

    db.session.add(user)
    commit_error = _safe_commit("Unable to create user.")
    if commit_error:
        return commit_error
    return jsonify({"success": True, "data": user.to_dict()}), 201


@api_bp.route("/users/<int:user_id>", methods=["GET"])
@_roles_required("admin")
def api_users_detail(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"success": True, "data": user.to_dict(include_profile=True)}), 200


@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@_roles_required("admin")
def api_users_update(user_id):
    user = User.query.get_or_404(user_id)
    payload, error = _load_json_payload()
    if error:
        return error

    if "email" in payload:
        email = _clean_text(payload.get("email")).lower()
        if not email:
            return _json_error("Email cannot be empty.", 400)
        if not _valid_email(email):
            return _json_error("Invalid email format.", 400)
        duplicate = User.query.filter(User.email == email, User.id != user.id).first()
        if duplicate:
            return _json_error("Email already exists.", 409)
        user.email = email

    if "password" in payload:
        password = payload.get("password") or ""
        if not password:
            return _json_error("Password cannot be empty.", 400)
        user.set_password(password)

    if "role" in payload:
        role_enum = _role_enum(payload.get("role"))
        if role_enum is None:
            return _json_error("Invalid role. Allowed: alumni, admin, director, registrar, osa.", 400)
        user.role = role_enum

    if "otp_verified" in payload:
        user.otp_verified = _parse_bool(payload.get("otp_verified"))
    if "email_verified" in payload:
        user.email_verified = _parse_bool(payload.get("email_verified"))
        user.email_verified_at = datetime.utcnow() if user.email_verified else None
    if "is_active" in payload:
        user.is_active = _parse_bool(payload.get("is_active"))
    if "approval_status" in payload:
        approval_status = (_clean_text(payload.get("approval_status")) or user.approval_status).lower()
        if approval_status not in {"pending", "approved", "rejected"}:
            return _json_error("approval_status must be pending, approved, or rejected.", 400)
        user.approval_status = approval_status

    commit_error = _safe_commit("Unable to update user.")
    if commit_error:
        return commit_error
    return jsonify({"success": True, "data": user.to_dict(include_profile=True)}), 200


@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@_roles_required("admin")
def api_users_delete(user_id):
    user = User.query.get_or_404(user_id)
    # Safe delete behavior: deactivate account instead of hard-deleting historical records.
    user.is_active = False
    user.approval_status = "rejected"
    commit_error = _safe_commit("Unable to deactivate user.")
    if commit_error:
        return commit_error
    return jsonify({"success": True, "message": "User account deactivated."}), 200


@api_bp.route("/jobs", methods=["GET"])
def api_jobs_list():
    query = Job.query.order_by(Job.posted_date.desc())
    if request.args.get("active"):
        query = query.filter(Job.is_active.is_(True))
    pagination = _paginate(query)
    return (
        jsonify(
            {
                "success": True,
                "data": [job.to_dict() for job in pagination.items],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@api_bp.route("/jobs", methods=["POST"])
@_roles_required("admin")
def api_jobs_create():
    payload, error = _load_json_payload()
    if error:
        return error

    title = _clean_text(payload.get("title"))
    company = _clean_text(payload.get("company"))
    if not title or not company:
        return _json_error("Title and company are required.", 400)
    salary_min, salary_min_error = _parse_optional_int(payload.get("salary_min"), "salary_min")
    if salary_min_error:
        return _json_error(salary_min_error, 400)
    salary_max, salary_max_error = _parse_optional_int(payload.get("salary_max"), "salary_max")
    if salary_max_error:
        return _json_error(salary_max_error, 400)

    job = Job(
        title=title,
        company=company,
        description=_clean_text(payload.get("description")) or None,
        requirements=_clean_text(payload.get("requirements")) or None,
        location=_clean_text(payload.get("location")) or None,
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=_clean_text(payload.get("job_type")) or "full-time",
        category=_clean_text(payload.get("category")) or None,
        is_active=_parse_bool(payload.get("is_active"), default=True),
    )

    db.session.add(job)
    commit_error = _safe_commit("Unable to create job.")
    if commit_error:
        return commit_error
    from app import dispatch_job_notifications

    dispatch_result = dispatch_job_notifications(
        job,
        action="created",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "data": job.to_dict(),
                "notification_dispatch": dispatch_result,
            }
        ),
        201,
    )


@api_bp.route("/jobs/<int:job_id>", methods=["GET"])
def api_jobs_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({"success": True, "data": job.to_dict()}), 200


@api_bp.route("/jobs/<int:job_id>", methods=["PUT"])
@_roles_required("admin")
def api_jobs_update(job_id):
    job = Job.query.get_or_404(job_id)
    payload, error = _load_json_payload()
    if error:
        return error

    if "title" in payload:
        title = _clean_text(payload.get("title"))
        if not title:
            return _json_error("Title cannot be empty.", 400)
        job.title = title
    if "company" in payload:
        company = _clean_text(payload.get("company"))
        if not company:
            return _json_error("Company cannot be empty.", 400)
        job.company = company
    if "description" in payload:
        job.description = _clean_text(payload.get("description")) or None
    if "requirements" in payload:
        job.requirements = _clean_text(payload.get("requirements")) or None
    if "location" in payload:
        job.location = _clean_text(payload.get("location")) or None
    if "salary_min" in payload:
        salary_min, salary_min_error = _parse_optional_int(payload.get("salary_min"), "salary_min")
        if salary_min_error:
            return _json_error(salary_min_error, 400)
        job.salary_min = salary_min
    if "salary_max" in payload:
        salary_max, salary_max_error = _parse_optional_int(payload.get("salary_max"), "salary_max")
        if salary_max_error:
            return _json_error(salary_max_error, 400)
        job.salary_max = salary_max
    if "job_type" in payload:
        job.job_type = _clean_text(payload.get("job_type")) or job.job_type
    if "category" in payload:
        job.category = _clean_text(payload.get("category")) or None
    if "is_active" in payload:
        job.is_active = _parse_bool(payload.get("is_active"))

    commit_error = _safe_commit("Unable to update job.")
    if commit_error:
        return commit_error
    from app import dispatch_job_notifications

    dispatch_result = dispatch_job_notifications(
        job,
        action="updated",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "data": job.to_dict(),
                "notification_dispatch": dispatch_result,
            }
        ),
        200,
    )


@api_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
@_roles_required("admin")
def api_jobs_delete(job_id):
    job = Job.query.get_or_404(job_id)
    job_snapshot = SimpleNamespace(title=job.title, company=job.company)
    db.session.delete(job)
    commit_error = _safe_commit("Unable to delete job.")
    if commit_error:
        return commit_error
    from app import dispatch_job_notifications

    dispatch_result = dispatch_job_notifications(
        job_snapshot,
        action="deleted",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "message": "Job deleted.",
                "notification_dispatch": dispatch_result,
            }
        ),
        200,
    )


@api_bp.route("/events", methods=["GET"])
def api_events_list():
    query = Event.query.order_by(Event.event_date.asc())
    if request.args.get("published"):
        query = query.filter(Event.is_published.is_(True))
    pagination = _paginate(query)
    return (
        jsonify(
            {
                "success": True,
                "data": [event.to_dict() for event in pagination.items],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@api_bp.route("/events", methods=["POST"])
@_roles_required("admin", "osa")
def api_events_create():
    payload, error = _load_json_payload()
    if error:
        return error

    title = _clean_text(payload.get("title"))
    event_date = _parse_datetime(payload.get("event_date"))
    if not title or not event_date:
        return _json_error("Title and event_date are required.", 400)

    contact_email = _clean_text(payload.get("contact_email")).lower() or None
    if contact_email and not _valid_email(contact_email):
        return _json_error("Invalid contact_email.", 400)

    event = Event(
        title=title,
        description=_clean_text(payload.get("description")) or None,
        event_type=_clean_text(payload.get("event_type")) or None,
        event_date=event_date,
        location=_clean_text(payload.get("location")) or None,
        venue=_clean_text(payload.get("venue")) or None,
        organizer=_clean_text(payload.get("organizer")) or None,
        contact_email=contact_email,
        is_published=_parse_bool(payload.get("is_published"), default=True),
    )
    db.session.add(event)
    commit_error = _safe_commit("Unable to create event.")
    if commit_error:
        return commit_error
    from app import dispatch_event_notifications

    dispatch_result = dispatch_event_notifications(
        event,
        action="created",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "data": event.to_dict(),
                "notification_dispatch": dispatch_result,
            }
        ),
        201,
    )


@api_bp.route("/events/<int:event_id>", methods=["GET"])
def api_events_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({"success": True, "data": event.to_dict()}), 200


@api_bp.route("/events/<int:event_id>", methods=["PUT"])
@_roles_required("admin", "osa")
def api_events_update(event_id):
    event = Event.query.get_or_404(event_id)
    payload, error = _load_json_payload()
    if error:
        return error

    if "title" in payload:
        title = _clean_text(payload.get("title"))
        if not title:
            return _json_error("Title cannot be empty.", 400)
        event.title = title
    if "description" in payload:
        event.description = _clean_text(payload.get("description")) or None
    if "event_type" in payload:
        event.event_type = _clean_text(payload.get("event_type")) or None
    if "event_date" in payload:
        parsed_event_date = _parse_datetime(payload.get("event_date"))
        if not parsed_event_date:
            return _json_error("Invalid event_date format.", 400)
        event.event_date = parsed_event_date
    if "location" in payload:
        event.location = _clean_text(payload.get("location")) or None
    if "venue" in payload:
        event.venue = _clean_text(payload.get("venue")) or None
    if "organizer" in payload:
        event.organizer = _clean_text(payload.get("organizer")) or None
    if "contact_email" in payload:
        contact_email = _clean_text(payload.get("contact_email")).lower() or None
        if contact_email and not _valid_email(contact_email):
            return _json_error("Invalid contact_email.", 400)
        event.contact_email = contact_email
    if "is_published" in payload:
        event.is_published = _parse_bool(payload.get("is_published"))

    commit_error = _safe_commit("Unable to update event.")
    if commit_error:
        return commit_error
    from app import dispatch_event_notifications

    dispatch_result = dispatch_event_notifications(
        event,
        action="updated",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "data": event.to_dict(),
                "notification_dispatch": dispatch_result,
            }
        ),
        200,
    )


@api_bp.route("/events/<int:event_id>", methods=["DELETE"])
@_roles_required("admin", "osa")
def api_events_delete(event_id):
    event = Event.query.get_or_404(event_id)
    event_snapshot = SimpleNamespace(title=event.title)
    db.session.delete(event)
    commit_error = _safe_commit("Unable to delete event.")
    if commit_error:
        return commit_error
    from app import dispatch_event_notifications

    dispatch_result = dispatch_event_notifications(
        event_snapshot,
        action="deleted",
        source_role=_current_role(),
        send_email=False,
    )
    return (
        jsonify(
            {
                "success": True,
                "message": "Event deleted.",
                "notification_dispatch": dispatch_result,
            }
        ),
        200,
    )


@api_bp.route("/notifications", methods=["GET"])
@_api_login_required
def api_notifications_list():
    query = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc())
    pagination = _paginate(query, default_per_page=25)
    return (
        jsonify(
            {
                "success": True,
                "data": [notification.to_dict() for notification in pagination.items],
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                },
            }
        ),
        200,
    )


@api_bp.route("/notifications/<int:notification_id>/read", methods=["PATCH"])
@_api_login_required
def api_notifications_mark_read(notification_id):
    notification = Notification.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first_or_404()
    notification.is_read = True
    commit_error = _safe_commit("Unable to update notification.")
    if commit_error:
        return commit_error
    return jsonify({"success": True, "data": notification.to_dict()}), 200


@api_bp.route("/notifications/read-all", methods=["POST"])
@_api_login_required
def api_notifications_mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update(
        {"is_read": True}, synchronize_session=False
    )
    commit_error = _safe_commit("Unable to mark notifications as read.")
    if commit_error:
        return commit_error
    return jsonify({"success": True, "message": "All notifications marked as read."}), 200


@export_bp.route("/users.csv", methods=["GET"])
@_roles_required("admin")
def export_users_csv():
    users = User.query.order_by(User.id.asc()).all()
    headers = [
        "id",
        "email",
        "role",
        "otp_verified",
        "email_verified",
        "is_active",
        "approval_status",
        "created_at",
        "last_login",
    ]
    rows = [
        [
            user.id,
            user.email,
            _role_slug(user.role),
            user.otp_verified,
            user.email_verified,
            user.is_active,
            user.approval_status,
            user.created_at.isoformat() if user.created_at else "",
            user.last_login.isoformat() if user.last_login else "",
        ]
        for user in users
    ]
    return _csv_response("users_export.csv", headers, rows)


@export_bp.route("/users.json", methods=["GET"])
@_roles_required("admin")
def export_users_json():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify({"success": True, "data": [user.to_dict(include_profile=True) for user in users]}), 200


@export_bp.route("/jobs.csv", methods=["GET"])
@_roles_required("admin")
def export_jobs_csv():
    jobs = Job.query.order_by(Job.id.asc()).all()
    headers = [
        "id",
        "title",
        "company",
        "job_type",
        "category",
        "location",
        "salary_min",
        "salary_max",
        "is_active",
        "posted_date",
    ]
    rows = [
        [
            job.id,
            job.title,
            job.company,
            job.job_type,
            job.category,
            job.location,
            job.salary_min,
            job.salary_max,
            job.is_active,
            job.posted_date.isoformat() if job.posted_date else "",
        ]
        for job in jobs
    ]
    return _csv_response("jobs_export.csv", headers, rows)


@export_bp.route("/jobs.json", methods=["GET"])
@_roles_required("admin")
def export_jobs_json():
    jobs = Job.query.order_by(Job.id.asc()).all()
    return jsonify({"success": True, "data": [job.to_dict() for job in jobs]}), 200


@export_bp.route("/events.csv", methods=["GET"])
@_roles_required("admin", "osa")
def export_events_csv():
    events = Event.query.order_by(Event.id.asc()).all()
    headers = [
        "id",
        "title",
        "event_type",
        "event_date",
        "location",
        "venue",
        "organizer",
        "contact_email",
        "is_published",
    ]
    rows = [
        [
            event.id,
            event.title,
            event.event_type,
            event.event_date.isoformat() if event.event_date else "",
            event.location,
            event.venue,
            event.organizer,
            event.contact_email,
            event.is_published,
        ]
        for event in events
    ]
    return _csv_response("events_export.csv", headers, rows)


@export_bp.route("/events.json", methods=["GET"])
@_roles_required("admin", "osa")
def export_events_json():
    events = Event.query.order_by(Event.id.asc()).all()
    return jsonify({"success": True, "data": [event.to_dict() for event in events]}), 200
