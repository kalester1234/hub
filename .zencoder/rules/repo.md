# Repository Overview

- **Project Name**: Medical Connect
- **Stack Summary**: Django application with Bootstrap-based front end, supporting patient, doctor, and admin flows. Uses SQLite locally.

## Key Structure
1. **Root Scripts**
   - `manage.py`: Django entry point
   - `check_users.py`, `create_admin.py`, `create_test_users.py`: helper scripts for admin user management
2. **Core Apps**
   - `accounts/`: Custom user models, forms, and views
   - `appointments/`: Appointment scheduling, doctor availability, and prescriptions
   - `dashboard/`: Role-specific dashboards for admin, doctor, and patient
   - `messaging/`: Notifications and internal messaging between users
3. **Project Settings**
   - `medical_connect/settings.py`: Django settings with custom auth and app registrations
   - `medical_connect/urls.py`: Root URL configuration
4. **Templates & Static**
   - `templates/`: Contains shared templates (`base.html`) and role-specific pages
   - `templates/admin/`: Customization for Django admin
   - `static/`: Shared static assets

## Testing
- `test_manage.py`: Basic test to verify Django management command configuration

## Deployment Notes
- `DEPLOYMENT_GUIDE.md` and `Procfile`: Guidance for deployment, likely to Heroku
- `requirements.txt`, `runtime.txt`: Python dependencies and runtime version

## Styling Conventions
- Bootstrap 5 classes used across templates
- Custom admin styles defined inline within templates
- Preference for clear typography and modern gradients

## Additional Notes
- Admin dashboard emphasizes appointment oversight and approvals
- Project encourages consistent use of full paths for tooling operations