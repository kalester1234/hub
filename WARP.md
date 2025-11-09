# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Medical Connect is a Django-based tele-health platform that coordinates patient appointment booking, doctor availability management, messaging, and admin oversight. The system supports three user roles: Patients, Doctors, and Admins.

## Development Commands

### Setup & Environment
```powershell
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create superuser/admin account
python manage.py createsuperuser
```

### Running the Application
```powershell
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 8080
```

### Database Management
```powershell
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell for database queries
python manage.py shell
```

### Testing
```powershell
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest test_manage.py

# Run tests with pytest (if configured)
pytest
```

### Management Commands
```powershell
# Send appointment reminders (custom management command)
python manage.py send_appointment_reminders
```

### Static Files
```powershell
# Collect static files for deployment
python manage.py collectstatic --noinput
```

## Architecture Overview

### Project Structure
```
medical_connect/          # Main Django project (settings, URLs, WSGI)
├── settings.py          # Central configuration with environment variable support
└── urls.py              # Root URL routing

accounts/                 # Authentication & user management
├── models.py            # CustomUser (role-based), DoctorProfile, PatientProfile
├── views.py             # Login, signup, profile management
└── urls.py              # Account-related routes

appointments/            # Scheduling & availability system
├── models.py            # Appointment, AvailabilitySlot, Prescription, DoctorLeave, AppointmentReminder
├── views.py             # Booking logic, availability management, prescription handling
├── forms.py             # Appointment booking and leave request forms
└── management/commands/ # Custom management commands (reminders)

dashboard/               # Role-based dashboards
├── views.py             # Doctor, patient, and admin dashboard aggregations
└── Analytics integration

messaging/               # Conversations & notifications
├── models.py            # Conversation, Message, Notification
└── views.py             # Real-time messaging and notification handling

templates/               # Django templates (HTML)
├── base.html            # Base template with navigation and chatbot widget
├── accounts/            # Login, signup, profile templates
├── appointments/        # Booking, browsing, detail templates
├── dashboard/           # Role-specific dashboard templates
└── messaging/           # Conversation and notification templates

static/                  # Static assets (CSS, JS, images)
media/                   # User-uploaded files (profile pictures, message attachments)
```

### User Roles & Permissions
- **Patient**: Book appointments, browse doctors, message doctors, view prescriptions
- **Doctor**: Manage availability, view/confirm appointments, write prescriptions, message patients
- **Admin**: Approve doctors, manage users, oversee all appointments, system analytics

### Key Architectural Patterns

#### Custom User Model
The system uses `accounts.CustomUser` extending Django's `AbstractUser` with a `role` field. All user-related operations should reference this model via `get_user_model()`.

#### Role-Based Access
- View functions use `@login_required` decorator and check `request.user.role`
- Dashboard redirects based on user role
- Templates conditionally render features based on role
- Never hardcode role checks as strings; use `user.role == 'doctor'` pattern

#### Appointment Booking Logic
The booking system has specific business rules:
1. **Auto-confirmation**: First 2 bookings for a time slot are auto-confirmed
2. **Pending queue**: 3rd booking enters pending status (requires admin approval)
3. **Slot cap**: Maximum 3 concurrent bookings per doctor/date/time
4. **Constraints**: Unique constraint on `(doctor, appointment_date, appointment_time)`

#### Availability Management
- Doctors define `AvailabilitySlot` objects per weekday
- "Everyday" feature clones slots across all weekdays using `update_or_create`
- Slots have `is_active` flag for temporary disabling
- Doctor leave requests block availability during specified date ranges

#### Notification System
Notifications are created for key events:
- Appointment requests, confirmations, completions, cancellations
- Doctor approval status changes
- New messages in conversations

Always create notifications when triggering user-facing state changes.

### Database Models Relationships

**User Profiles**: `CustomUser` → `DoctorProfile` (one-to-one) or `PatientProfile` (one-to-one)

**Appointments**: `Appointment` links `doctor` (CustomUser) ↔ `patient` (CustomUser)
- Has one `Prescription` (one-to-one)
- Each `Prescription` has multiple `PrescriptionItem` objects

**Messaging**: `Conversation` links doctor-patient pairs
- Has many `Message` objects
- Optional link to `Appointment`

**Scheduling**: `AvailabilitySlot` defines doctor's weekly availability
- Multiple slots per doctor
- Unique constraint on `(doctor, day_of_week, start_time)`

## Coding Guidelines

### Environment Variables
The project uses `python-decouple` for configuration. Settings are loaded from `.env` file:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Boolean for debug mode
- `ENV`: 'development' or 'production'
- `DATABASE_URL`: PostgreSQL connection string (production only)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email configuration

Never commit `.env` files or hardcode secrets.

### Database Queries
- Use `select_related()` for single-valued relationships (ForeignKey, OneToOneField)
- Use `prefetch_related()` for multi-valued relationships (reverse ForeignKey, ManyToMany)
- Example: `Appointment.objects.filter(doctor=doctor).select_related('patient').prefetch_related('prescription__items')`

### Forms & Validation
- Use Django forms for all user input
- Custom validation goes in `clean()` or `clean_<field>()` methods
- Forms automatically include CSRF protection

### Templates
- Extend `base.html` for consistent navigation and layout
- Chatbot widget is automatically hidden for doctor role in `base.html`
- Use template tags: `{% load static %}` for static files
- Access user role via `request.user.role` in templates

### Deployment Configuration
- Development uses SQLite (`db.sqlite3`)
- Production switches to PostgreSQL when `ENV=production`
- WhiteNoise serves static files in production
- Gunicorn is the WSGI server (specified in `Procfile`)
- Email backend: console (dev) vs SMTP (production)

### Migration Workflow
1. Modify models in `models.py`
2. Run `python manage.py makemigrations`
3. Review generated migration files
4. Apply with `python manage.py migrate`
5. Never delete migration files once applied to production

### URL Naming Convention
All URL patterns use named routes:
- Reference in views: `redirect('dashboard')`
- Reference in templates: `{% url 'dashboard' %}`
- Namespacing: Apps use URL namespacing where applicable

### Custom Management Commands
Located in `<app>/management/commands/`. Example:
- `appointments/management/commands/send_appointment_reminders.py`

Run with: `python manage.py <command_name>`

## Important Business Logic

### Appointment Status Workflow
```
pending → confirmed → completed
       ↘ cancelled
```

### Slot Booking Algorithm (in `appointments/views.book_appointment`)
```python
slot_bookings = Appointment.objects.filter(
    doctor=doctor,
    appointment_date=date,
    appointment_time=time,
    status__in=['pending', 'confirmed']
).count()

if slot_bookings < 2:
    status = 'confirmed'  # Auto-confirm
elif slot_bookings == 2:
    status = 'pending'    # Admin review needed
else:
    # Reject: slot full
```

### Everyday Availability Feature
When a doctor sets availability with "apply_everyday", the system:
1. Loops through all 7 days of week
2. Calls `AvailabilitySlot.objects.update_or_create()` per day
3. Uses same start_time, end_time, slot_duration

This ensures consistent availability without manual repetition.

## Testing Approach

The codebase uses Python's `unittest` framework. Tests are located in root directory files like `test_manage.py`, `test_db.py`, `test_view.py`.

When writing tests:
- Use `unittest.TestCase` base class
- Mock external dependencies with `unittest.mock.patch`
- Test business logic separately from Django views when possible
- Use Django's test client for integration tests: `self.client.get('/url/')`

## Deployment Notes

### Render Deployment (Primary)
See `DEPLOYMENT_GUIDE.md` for full instructions. Key points:
- Set environment variables in Render dashboard
- `Procfile` defines web and release commands
- PostgreSQL database is optional but recommended
- Automatic deployments on GitHub push

### Environment Setup Checklist
- [ ] `SECRET_KEY` set (generate new for production)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] `DATABASE_URL` set (if using PostgreSQL)
- [ ] Email credentials configured (if using email features)

## Feature Flags & Configuration

### Chatbot Widget
The chatbot is visible to patients but hidden from doctors via template logic in `base.html`. Modify the visibility condition if requirements change.

### Email Backend
- Development: Console backend (prints to terminal)
- Production: SMTP backend (requires email credentials)

### Admin Dashboard Analytics
Admin dashboard includes appointment analytics and doctor performance metrics. Chart data is prepared in `dashboard/views.admin_dashboard()`.

## Common Patterns

### Creating Notifications
```python
from messaging.models import Notification

Notification.objects.create(
    user=recipient_user,
    notification_type='appointment_confirmed',
    title='Appointment Confirmed',
    description='Your appointment has been confirmed.',
    related_appointment=appointment
)
```

### Checking User Role
```python
# In views
if request.user.role == 'doctor':
    # Doctor-specific logic
    
# In templates
{% if request.user.role == 'patient' %}
    <!-- Patient-specific UI -->
{% endif %}
```

### Handling Appointments with Prescriptions
```python
# Prefetch to avoid N+1 queries
appointments = Appointment.objects.filter(
    doctor=doctor
).select_related('patient').prefetch_related('prescription__items')

# Check if prescription exists
for appointment in appointments:
    if hasattr(appointment, 'prescription'):
        # Has prescription
```

## Troubleshooting

### Migration Issues
If migrations fail:
1. Check for conflicting migrations: `python manage.py showmigrations`
2. Ensure all apps have up-to-date migrations
3. For SQLite issues, backup `db.sqlite3` and recreate database

### Import Errors
Django apps must be in `INSTALLED_APPS` in `settings.py`. Current apps:
- `accounts`
- `appointments`
- `messaging`
- `dashboard`

### Static Files Not Loading
1. Ensure `DEBUG=True` in development
2. Check `STATIC_URL` and `STATICFILES_DIRS` in settings
3. Run `collectstatic` for production

### Permission Errors
- Verify user has correct role assigned
- Check view decorators (`@login_required`)
- Ensure role-based logic in view matches URL access

## Future Enhancements (from TODO.md)

Currently in progress:
- Email templates for appointment reminders
- Doctor dashboard leave status display
- Admin interface for prescription templates
- Chart.js integration for analytics
- Template selection for prescription creation

When implementing these features, follow existing patterns in corresponding apps.
