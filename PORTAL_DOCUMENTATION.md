# Role-Based Portal Documentation

This document explains the role-based portal system in the WVSU Pototan Online Alumni Tracking and Graduate Tracer Study System. The current application is implemented with Flask, Jinja templates, SQLAlchemy models, shared CSS, and role-based navigation data in `app.py`.

The UI refactor centralizes the internal dashboard shell in `templates/base.html` and `templates/_dashboard_sidebar.html`. Internal pages opt into the shared dashboard layout with `use_dashboard_layout`, so the sidebar remains persistent across dashboards, management pages, analytics, notifications, exports, jobs, events, and nested internal routes.

## Shared Portal Architecture

### Shared Layout Components

- `templates/base.html`: Main page shell. It keeps the public navbar, flash messages, footer, theme toggle, scripts, and the conditional dashboard wrapper.
- `templates/_dashboard_sidebar.html`: Shared sidebar wrapper used by all authenticated dashboard pages. It renders the portal navigation and a user/profile summary.
- `templates/_sidebar_nav_sections.html`: Single source of truth for sidebar links. It loops through `current_portal_navigation` from `app.py`.
- `templates/_dashboard_notifications.html`: Reusable dashboard notification preview panel.
- `PORTAL_NAVIGATION` in `app.py`: Defines sidebar sections and links per role.
- `ROLE_PORTALS` in `app.py`: Defines supported portal roles and their dashboard templates.
- `role_required()` in `app.py`: Protects pages by role.
- `apply_security_headers()` in `app.py`: Adds shared browser security headers.
- `static/css/style.css`: Shared visual system, dashboard layout, cards, tables, forms, dark mode, and role accent styling.

### Shared Data Models

- `User`: Login account, role, password, OTP status, email verification, approval state, and activity metadata.
- `AlumniProfile`: Alumni personal, education, family, enrollment, employment, skills, and photo information.
- `TracerSurvey`: Graduate tracer survey answers and satisfaction ratings.
- `Job`: Job posting records.
- `Event`: Event calendar records.
- `EventRSVP`: Event attendance responses.
- `Notification`: In-app notifications sent to users.
- `PasswordReset`: Password reset tokens.
- `EmailVerificationToken`: Email verification links.
- `SystemLog`: System activity records.
- `Report`: Report metadata.

## Admin Portal

### 1. Purpose

The Admin Portal is for system administrators who manage the entire platform. Admin users can control accounts, alumni records, surveys, jobs, events, exports, password support, approvals, notifications, and system reset operations.

### 2. Key Features

- Dashboard: Shows total alumni, surveys, jobs, events, pending approvals, RSVP counts, employment rate, recent notifications, and recent activity.
- Notifications: Shows in-app system, job, and event notifications.
- Analytics: Shows employment status, graduates by year, degree distribution, survey averages, and summary metrics.
- Alumni management: Lists alumni records, supports searching by name, degree, student ID, and email, and allows editing or deleting alumni records.
- Job management: Creates, edits, deletes, and broadcasts job posts.
- Event management: Creates, edits, deletes, and broadcasts events.
- RSVP analytics: Shows RSVP counts by event and attendee detail lists.
- RSVP export: Downloads event RSVP data as CSV.
- Account approvals: Approves or rejects non-alumni account registrations.
- Survey review: Lists tracer survey responses.
- Data exports: Exports users, jobs, and events as CSV or JSON.
- Password management: Lists users, resets user passwords, deletes users, and bulk-deletes eligible alumni accounts.
- System reset: Clears platform data with confirmation and can retain the default admin account.

### 3. Pages and Routes

- `/portal/admin/dashboard`: Main admin dashboard.
- `/admin`: Legacy admin overview page.
- `/notifications`: Notification inbox.
- `/notifications/<notification_id>/read`: Marks one notification as read.
- `/notifications/read-all`: Marks all notifications as read.
- `/analytics`: Analytics dashboard.
- `/admin/alumni`: Alumni management list.
- `/admin/alumni/edit/<alumni_id>`: Edit an alumni profile.
- `/admin/alumni/delete/<alumni_id>`: Delete an alumni record or linked alumni account.
- `/admin/jobs`: Job management list.
- `/admin/jobs/add`: Create a job post.
- `/admin/jobs/edit/<job_id>`: Edit a job post.
- `/admin/jobs/delete/<job_id>`: Delete a job post.
- `/admin/events`: Event management list.
- `/admin/events/add`: Create an event.
- `/admin/events/edit/<event_id>`: Edit an event.
- `/admin/events/delete/<event_id>`: Delete an event.
- `/admin/events/rsvp-analytics`: RSVP analytics dashboard.
- `/admin/events/<event_id>/rsvps/export`: Export RSVP rows for one event.
- `/admin/account-approvals`: Review non-alumni account requests.
- `/admin/account-approvals/<user_id>/approve`: Approve a privileged account.
- `/admin/account-approvals/<user_id>/reject`: Reject a privileged account.
- `/admin/surveys`: Survey response list.
- `/admin/surveys/delete/<survey_id>`: Delete a survey response.
- `/admin/exports`: Data Export Center.
- `/exports/users.csv`, `/exports/users.json`: User exports.
- `/exports/jobs.csv`, `/exports/jobs.json`: Job exports.
- `/exports/events.csv`, `/exports/events.json`: Event exports.
- `/admin/password-management`: User password and account management.
- `/admin/users/<user_id>/reset-password`: Reset a user's password.
- `/admin/users/<user_id>/delete`: Delete one user.
- `/admin/users/bulk-delete`: Bulk-delete eligible alumni users.
- `/admin/system-reset`: System reset page.
- `/reset-password`: Signed-in password reset page.

### 4. Components Used

- Shared dashboard shell: Keeps the sidebar visible across admin pages.
- Sidebar navigation: Uses `PORTAL_NAVIGATION["admin"]`.
- Portal hero: Lightweight dashboard header with admin label, title, subtitle, and icon.
- Portal cards: Display counts and status values.
- Table containers: Used for alumni, jobs, events, surveys, approvals, users, and RSVP analytics.
- Form sections: Used for add/edit/reset/system reset forms.
- Dashboard notifications panel: Shows recent notifications.
- Chart cards: Used on analytics pages.

### 5. Data and Interactions

The Admin Portal reads and writes nearly every major model: `User`, `AlumniProfile`, `TracerSurvey`, `Job`, `Event`, `EventRSVP`, `Notification`, `PasswordReset`, `EmailVerificationToken`, `SystemLog`, and `Report`. It also dispatches in-app notifications and optional email notifications when jobs or events are created or updated.

Admin actions affect other portals. For example, creating a job notifies alumni, director, registrar, OSA, and admin users. Approving privileged accounts controls whether Director, Registrar, and OSA users can fully access their portals.

### 6. Access Control

Admin-only pages use `@role_required("admin")`. Some pages are shared with other roles, such as analytics with Director and event management with OSA. Admin accounts require OTP verification, email verification when enabled, and approval status checks.

## Alumni Portal

### 1. Purpose

The Alumni Portal is for graduates and alumni users. It lets alumni maintain their profile, complete graduate tracer information, answer surveys, browse jobs, view events, RSVP, and see notifications.

### 2. Key Features

- Dashboard: Shows profile completion, survey status, alumni network size, active jobs, and recent notifications.
- Profile editing: Updates personal, education, contact, social, employment, skills, and volunteer information.
- 4-Part Alumni Form: Collects personal information, education, family background, and enrollment or employment details.
- Profile view: Displays the completed alumni module profile.
- Tracer survey: Collects school experience, skills, employment, satisfaction, and recommendation ratings.
- My Survey: Shows the latest submitted survey.
- Jobs: Lets alumni browse active job opportunities.
- Events: Lets alumni view published upcoming events.
- RSVP: Lets eligible users mark attending or not attending.
- Alumni directory: Lets users browse and search alumni profiles.
- Notifications: Shows job, event, and system notices.
- Password reset: Lets signed-in users change their password.

### 3. Pages and Routes

- `/portal/alumni/dashboard`: Main alumni dashboard.
- `/dashboard`: Redirects to the active role dashboard.
- `/dashboard/overview`: Alumni dashboard overview with events and jobs.
- `/notifications`: Notification inbox.
- `/my-profile`: Read-only alumni profile view.
- `/profile`: Edit alumni profile.
- `/alumni-module`: Redirects to the alumni module dashboard.
- `/alumni-module/dashboard`: Completion dashboard for the 4-part form.
- `/alumni-module/form`: Main 4-part alumni form.
- `/alumni-module/profile`: Profile view for alumni module data.
- `/alumni-module/photo/delete`: Deletes the uploaded profile photo.
- `/survey`: Create or update tracer survey response.
- `/my-survey`: View submitted survey.
- `/jobs`: Browse active jobs.
- `/jobs/<job_id>`: View job details.
- `/events`: Browse upcoming published events.
- `/events/<event_id>`: View event details.
- `/events/<event_id>/rsvp`: Submit event RSVP.
- `/alumni`: Alumni directory.
- `/reset-password`: Signed-in password reset page.

### 4. Components Used

- Shared dashboard shell: Keeps alumni navigation available across profile, module, survey, job, event, and notification pages when signed in.
- Sidebar navigation: Uses `PORTAL_NAVIGATION["alumni"]`.
- Portal hero: Used on the alumni dashboard only, with no embedded action buttons.
- Portal cards and progress bars: Show completion and survey state.
- Form sections and stepper controls: Used by profile and alumni module forms.
- Photo preview controls: Used for profile photo upload.
- Dashboard notification panel: Shows recent notices.
- Job and event cards: Show public and signed-in browsing content.

### 5. Data and Interactions

The Alumni Portal reads and writes the signed-in user's `User` and `AlumniProfile` records. It writes `TracerSurvey` responses and `EventRSVP` records. It reads active `Job` and published `Event` records created by admins or OSA. It receives `Notification` records created by admin, OSA, or system actions.

### 6. Access Control

Alumni-only internal pages use `@role_required("alumni")`. Public job, event, and alumni directory pages are visible to guests, but signed-in users now see them inside the dashboard shell. RSVP submission requires login and a role included in `RSVP_ALLOWED_ROLES`; alumni and admin access are always enabled by the current helper.

## OSA Portal

### 1. Purpose

The OSA Portal is for the Office of Student Affairs. It focuses on student and alumni engagement through events, RSVP monitoring, event reports, notifications, and data exports.

### 2. Key Features

- Dashboard: Shows upcoming published events, RSVP counts, and recent notifications.
- Notifications: Shows event, job, and system updates.
- Event management: Lets OSA create, edit, publish, and delete events.
- RSVP analytics: Tracks attendance responses by event.
- RSVP export: Downloads RSVP records for event reporting.
- Data Export Center: Allows event exports.
- Password reset: Lets signed-in OSA users update their password.

### 3. Pages and Routes

- `/portal/osa/dashboard`: Main OSA dashboard.
- `/notifications`: Notification inbox.
- `/admin/events`: Event management list shared with admin.
- `/admin/events/add`: Create an event.
- `/admin/events/edit/<event_id>`: Edit an event.
- `/admin/events/delete/<event_id>`: Delete an event.
- `/admin/events/rsvp-analytics`: RSVP analytics.
- `/admin/events/<event_id>/rsvps/export`: RSVP CSV export.
- `/admin/exports`: Data Export Center.
- `/exports/events.csv`, `/exports/events.json`: Event exports.
- `/reset-password`: Signed-in password reset page.

### 4. Components Used

- Shared dashboard shell and sidebar.
- Sidebar navigation from `PORTAL_NAVIGATION["osa"]`.
- Portal hero on the OSA dashboard.
- Portal cards for event and RSVP summary data.
- Event management tables and forms.
- RSVP analytics tables.
- Dashboard notifications panel.

### 5. Data and Interactions

The OSA Portal reads and writes `Event` records and reads `EventRSVP` data. When events are created, the notification dispatch system can notify active, verified, approved users across roles. OSA can export event data for reporting.

### 6. Access Control

OSA dashboard access is role-specific. Event management, RSVP analytics, and exports are protected by `@role_required("admin", "osa")`, so OSA and Admin can both access those workflows. OSA accounts require approval because OSA is a privileged role.

## Registrar Portal

### 1. Purpose

The Registrar Portal is for staff responsible for alumni records and profile verification. It gives registrar users a focused view of alumni records without full system administration rights.

### 2. Key Features

- Dashboard: Shows pending profile verification counts and verified alumni counts.
- Notifications: Shows system, job, and event notifications.
- Alumni records: Lists alumni records and allows searching.
- Alumni editing: Allows registrar users to update key profile fields.
- Password reset: Lets signed-in registrar users update their password.

### 3. Pages and Routes

- `/portal/registrar/dashboard`: Main registrar dashboard.
- `/notifications`: Notification inbox.
- `/admin/alumni`: Alumni record list shared with admin.
- `/admin/alumni/edit/<alumni_id>`: Edit an alumni profile.
- `/reset-password`: Signed-in password reset page.

### 4. Components Used

- Shared dashboard shell and sidebar.
- Sidebar navigation from `PORTAL_NAVIGATION["registrar"]`.
- Portal hero on the registrar dashboard.
- Portal cards for pending and verified records.
- Alumni table and edit form.
- Dashboard notifications panel.

### 5. Data and Interactions

The Registrar Portal reads `AlumniProfile` and linked `User` data. It writes selected alumni profile fields through the shared admin edit route. It does not control approvals, jobs, events, or system reset.

### 6. Access Control

Registrar dashboard access is role-specific. Alumni listing and edit routes use `@role_required("admin", "registrar")`. Deleting alumni remains admin-only. Registrar accounts require approval because Registrar is a privileged role.

## Director Portal

### 1. Purpose

The Director Portal is for institutional leadership. It provides a high-level view of alumni outcomes, employment metrics, survey performance, and academic program trends.

### 2. Key Features

- Dashboard: Shows employment rate, survey response rate, and recent notifications.
- Analytics: Displays charts for employment status, graduates by year, degree distribution, and survey rating averages.
- Survey insights: Lists tracer survey responses.
- Notifications: Shows updates from the system.
- Password reset: Lets signed-in director users update their password.

### 3. Pages and Routes

- `/portal/director/dashboard`: Main director dashboard.
- `/analytics`: Analytics dashboard shared with admin.
- `/admin/surveys`: Survey insights page shared with admin.
- `/notifications`: Notification inbox.
- `/reset-password`: Signed-in password reset page.

### 4. Components Used

- Shared dashboard shell and sidebar.
- Sidebar navigation from `PORTAL_NAVIGATION["director"]`.
- Portal hero on the director dashboard.
- Portal cards for performance metrics.
- Chart cards on analytics.
- Survey tables.
- Dashboard notifications panel.

### 5. Data and Interactions

The Director Portal primarily reads `AlumniProfile`, `TracerSurvey`, and `Job` summary data. It does not create jobs, events, or accounts. It receives notifications generated by admin or OSA actions.

### 6. Access Control

Director dashboard access is role-specific. Analytics and survey insights use `@role_required("admin", "director")`. Director accounts require approval because Director is a privileged role.

## CSC/Council Portal

### 1. Purpose

There is no CSC or Council portal implemented in the current codebase. The current `UserRole` enum only contains `alumni`, `admin`, `director`, `registrar`, and `osa`.

If added later, a CSC/Council portal would likely support student council announcements, engagement activities, event coordination, and communication with alumni or student affairs staff.

### 2. Key Features

No CSC/Council features exist yet in the actual code.

A future implementation would require:

- A new role in `UserRole`.
- A new entry in `ROLE_PORTALS`.
- Navigation entries in `PORTAL_NAVIGATION`.
- Login and registration templates under `templates/portals/<role>/`.
- Dashboard route handling through the existing `/portal/<role>/dashboard` route.
- Role permissions added to `role_required()` usage where needed.

### 3. Pages and Routes

No CSC/Council routes exist yet.

Potential future routes could include:

- `/portal/csc/dashboard`
- `/portal/csc/login`
- `/portal/csc/register`
- `/council/events`
- `/council/announcements`

### 4. Components Used

No CSC/Council components exist yet. The new shared dashboard shell is ready to support a future portal once the role is added to the role and navigation configuration.

### 5. Data and Interactions

No CSC/Council data interactions exist yet. A future portal could read events and notifications and write council announcements or engagement records if new models are added.

### 6. Access Control

No CSC/Council access control exists yet. A future role should follow the same pattern as OSA, Registrar, and Director: OTP verification, email verification when enabled, approval status checks, active session validation, and role-protected routes.

## Authentication and Security Flow

1. User selects a portal.
2. User registers or logs in through `/portal/<role>/register` or `/portal/<role>/login`.
3. The system validates email and password.
4. The system issues an OTP.
5. The user verifies OTP at `/verify-otp`.
6. If email verification is enabled, the user verifies a link at `/verify-email/<token>`.
7. Privileged roles wait for admin approval if required.
8. Once active, the user enters the role dashboard.
9. `validate_active_session()` checks that the session user and role still match.
10. `role_required()` prevents users from opening pages outside their allowed role.

## Overall Portal Flowchart

```text
Public Website
  |
  +-- Portal Selection
        |
        +-- Alumni Login/Register
        |     |
        |     +-- OTP + Email Verification
        |     +-- Alumni Dashboard
        |           +-- Profile and 4-Part Form
        |           +-- Tracer Survey
        |           +-- Jobs, Events, RSVP
        |           +-- Notifications
        |
        +-- Admin Login/Register
        |     |
        |     +-- OTP + Email Verification + Approval
        |     +-- Admin Dashboard
        |           +-- Users and Account Approvals
        |           +-- Alumni Records
        |           +-- Jobs and Events
        |           +-- Surveys, Analytics, Exports
        |           +-- System Reset
        |
        +-- Director Login/Register
        |     |
        |     +-- OTP + Email Verification + Approval
        |     +-- Director Dashboard
        |           +-- Analytics
        |           +-- Survey Insights
        |
        +-- Registrar Login/Register
        |     |
        |     +-- OTP + Email Verification + Approval
        |     +-- Registrar Dashboard
        |           +-- Alumni Records
        |           +-- Profile Verification
        |
        +-- OSA Login/Register
              |
              +-- OTP + Email Verification + Approval
              +-- OSA Dashboard
                    +-- Event Management
                    +-- RSVP Analytics
                    +-- Event Exports

Shared Services Used By All Portals
  |
  +-- User Accounts and Roles
  +-- OTP and Email Verification
  +-- Approval Status
  +-- Notifications
  +-- Shared Dashboard Layout and Sidebar
  +-- Database Models
  +-- Security Headers and Session Validation
```

