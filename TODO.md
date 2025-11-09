# New Features Implementation Plan

## 1. Appointment Reminders via Email
- [x] Add AppointmentReminder model to appointments/models.py
- [x] Create management command `send_appointment_reminders.py` for sending reminders
- [x] Update medical_connect/settings.py to configure SMTP email backend
- [ ] Add email templates for reminders
- [x] Test email sending in development

## 2. Doctor Leave Management System
- [x] Create forms for leave requests in appointments/forms.py
- [x] Add views for leave management in appointments/views.py (request, approve/reject)
- [ ] Update doctor dashboard template to show leave status
- [x] Add notifications for leave approvals/rejections
- [x] Update URLs for leave management

## 3. Prescription Templates
- [x] Add PrescriptionTemplate and PrescriptionTemplateItem models to appointments/models.py
- [ ] Create admin interface for managing templates
- [ ] Update prescription creation view to allow selecting from templates
- [ ] Add template selection to prescription forms

## 4. Appointment Analytics Dashboard
- [x] Extend dashboard/views.py with analytics data (monthly counts, doctor performance)
- [ ] Add Chart.js library to static files
- [ ] Update admin dashboard template with analytics charts
- [ ] Create new template sections for analytics

## Followup Steps
- [x] Run migrations for new models
- [ ] Install any new dependencies (e.g., Chart.js)
- [ ] Set up cron job for reminders
- [ ] Test all new features end-to-end
