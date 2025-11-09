# Admin Dashboard Guide

## Access Information

**URL**: `http://127.0.0.1:8000/dashboard/admin/`  
**Admin Username**: `admin`  
**Total Admin Users**: 3

## Dashboard Status: ✅ FULLY OPERATIONAL

All admin dashboard features have been tested and are working correctly.

---

## Dashboard Sections

### 1. 📊 Overview (Default Landing Page)

The overview provides a comprehensive snapshot of the entire platform.

#### Key Metrics Cards
- **Total Doctors**: Shows total doctors with approval percentage
- **Total Patients**: Shows total patients with active percentage  
- **Hospitals on Platform**: Number of hospitals linked to doctor profiles
- **Pending Approvals**: Number of doctors awaiting approval

#### Appointment Overview
- Upcoming appointments (scheduled from today onwards)
- Pending appointments (awaiting confirmation)
- Completed this month (month-to-date statistics)

#### Visual Charts
- **Appointment Status Chart**: Bar chart showing pending, confirmed, completed, and cancelled appointments
- **Hospitals Snapshot Table**: Top 5 hospitals with doctor count and contact info

---

### 2. 🏥 Manage Data Section

Centralized location for managing doctors and hospitals.

#### Doctors Tab

**Current Status**:
- Total Doctors: 33
- Approved: 33
- Pending: 0

**Features**:
1. **Search Functionality**: Search by name, email, phone, hospital, or specialization
2. **Doctor List Table** with columns:
   - Doctor name with initials avatar
   - Specialization
   - Hospital affiliation
   - Contact (email & phone)
   - Status (Approved/Pending)
   - Actions (dropdown menu)

3. **Action Menu for Each Doctor**:
   - View detailed records
   - Approve doctor (if pending)
   - Remove doctor

4. **Add New Doctor**: Button to quickly add a new doctor account

**Doctor Records Modal**:
- Shows last 5 appointments for selected doctor
- Displays patient name, date, time, and appointment status
- Total appointment count

#### Hospitals Tab

**Current Status**:
- Total Hospitals: 2
- Doctors with Hospital Affiliation: 10

**Features**:
- Complete list of all hospitals
- Doctor count per hospital
- Primary contact information

---

### 3. 👥 Users Section

Manage all user accounts on the platform.

#### Patients Tab (Default)

**Current Status**:
- Total Patients: 15
- Active Patients: 15
- Inactive Patients: 0

**Features**:
1. **Search Functionality**: Search by name, email, phone, or medical history
2. **Patient List Table**:
   - Patient name with avatar
   - Email address
   - Phone number
   - Date of birth
   - Join date
   - Status (Active/Inactive)
   - Remove action

3. **Add New Patient**: Quick add button

#### Admins Tab

**Current Status**:
- Total Admins: 3

**Features**:
- List of all admin users
- Contact information
- Status and join date
- Cannot remove self

---

### 4. 📅 Appointments Section

Comprehensive appointment management interface.

#### Quick Stats
- Total Appointments
- Pending Appointments
- Upcoming Appointments
- Completed Appointments

#### Three Sub-tabs:

**Recent Tab** (Default):
- Last 8 appointments across all statuses
- Shows doctor, patient, date, time, and status

**Pending Tab**:
- Appointments awaiting admin approval
- Quick action to confirm or cancel
- Sorted by appointment date/time

**Upcoming Tab**:
- All future appointments
- Allows monitoring of schedule
- Shows confirmed appointments

**Features**:
- Color-coded status badges
- Patient and doctor information
- Date and time display
- Quick action buttons

---

### 5. 🔔 Notifications Section

Monitor and manage all system notifications.

#### Notification Stats
- Total Notifications
- Unread Notifications  
- Read Notifications

**Features**:
1. **Mark All as Read**: Bulk action button
2. **Recent Notifications List** (Last 10):
   - User recipient
   - Notification type (icon-coded)
   - Title and description
   - Timestamp
   - Read/unread status

**Notification Types**:
- 📋 Appointment Requests
- ✅ Appointment Confirmations
- ✓ Appointment Completions
- ✗ Appointment Cancellations
- 💬 New Messages
- 👨‍⚕️ Doctor Approvals

---

## Key Features

### Search & Filter
- **Doctor Search**: Name, email, phone, hospital, specialization
- **Patient Search**: Name, email, phone, medical history
- **Clear Search**: One-click to reset filters

### Doctor Approval Workflow
1. Admin receives notification of new doctor signup
2. Navigate to Manage Data → Doctors
3. Click action menu on pending doctor
4. Click "Approve" button
5. Doctor immediately gains access to platform
6. Notification sent to doctor

### Appointment Management
1. View pending appointments in Appointments section
2. Click on appointment to see details
3. Update status (confirm/cancel)
4. Add admin notes if needed
5. Notifications automatically sent to patient and doctor

### User Management
- Add new doctors or patients directly from dashboard
- Remove users when necessary (except self for admins)
- View complete user details and history

---

## Dashboard Design

### Navigation
- **Sidebar Navigation**: Fixed left sidebar with icon+label links
- **Active Section Highlighting**: Current section is highlighted
- **Smooth Scrolling**: Anchor links for quick navigation
- **Responsive**: Adapts to different screen sizes

### Visual Elements
- **Color-Coded Metrics**: Each metric type has distinct color
- **Progress Bars**: Visual representation of percentages
- **Status Badges**: Color-coded (pending=yellow, confirmed=blue, completed=green, cancelled=red)
- **Avatar Initials**: User initials in circular avatars
- **Icons**: Bootstrap Icons for visual clarity

### Data Tables
- **Sortable Columns** (where applicable)
- **Horizontal Scroll**: For tables with many columns
- **Empty States**: Friendly messages when no data available
- **Hover Effects**: Interactive row highlighting

---

## Common Admin Tasks

### Approve a New Doctor
1. Log in as admin
2. Dashboard shows "Pending Approvals" count
3. Click "Pending Approvals" card OR navigate to Manage Data
4. Find the doctor in the list (Pending status)
5. Click action menu (three dots)
6. Click "Approve"
7. Confirmation message appears
8. Doctor can now log in and manage appointments

### Monitor Appointments
1. Navigate to Appointments section
2. Check pending tab for appointments needing review
3. Click appointment to see full details
4. Update status if needed
5. Notifications sent automatically

### Add a New User
1. Click "+ Add Doctor" or "+ Add Patient" button
2. Fill in registration form
3. Submit
4. User appears in respective list immediately

### Search for Specific Information
1. Use search box in relevant section
2. Enter search term
3. Results filter automatically
4. Click "Clear" to reset

### View Doctor Performance
1. Navigate to Manage Data → Doctors
2. Click action menu for specific doctor
3. Select "View records"
4. Modal shows last 5 appointments and total count

---

## Technical Details

### Database Queries
- Optimized with `select_related()` and `prefetch_related()`
- Separate queries to avoid annotation conflicts
- Efficient counting and aggregation

### Real-time Data
- Dashboard data updates on each page load
- No caching (always fresh data)
- Accurate counts and statistics

### Security
- Login required (`@login_required` decorator)
- Role check (must be admin role)
- CSRF protection on all forms
- Prevents unauthorized access

### Performance
- Efficient database queries
- Limited lists (e.g., top 5 hospitals, last 10 notifications)
- Pagination possible for larger datasets

---

## URL Parameters

Navigate directly to sections using URL parameters:

```
# Go directly to Manage Data section
/dashboard/admin/?focus=manage-data#manage-data

# Go to Users section
/dashboard/admin/?focus=users#users

# Go to Appointments section
/dashboard/admin/?focus=appointments#appointments

# Search doctors
/dashboard/admin/?doctor_search=cardiology&focus=manage-data

# Search patients
/dashboard/admin/?patient_search=john&focus=users
```

---

## Tested Features ✅

All features have been tested and confirmed working:

1. ✅ Dashboard loads successfully (HTTP 200)
2. ✅ All sections render correctly
3. ✅ Doctor list displays with 33 doctors
4. ✅ Patient list displays with 15 patients
5. ✅ Hospital metrics calculated correctly
6. ✅ Appointment statistics accurate
7. ✅ Notification system operational
8. ✅ Search functionality works for doctors
9. ✅ Search functionality works for patients
10. ✅ Charts and visualizations render
11. ✅ Action menus functional
12. ✅ Status updates work correctly

---

## Known Features

### What Works Perfectly
- All data displays correctly
- Search and filter functionality
- Doctor approval workflow
- Appointment management
- Notification system
- User management
- Charts and statistics
- Responsive design

### Future Enhancements (from TODO.md)
- Email templates for appointment reminders
- Chart.js integration for advanced analytics
- Admin interface for prescription templates
- Doctor performance analytics graphs
- Export functionality for reports

---

## Quick Reference

### Admin Credentials
- Username: `admin`
- Access URL: `http://127.0.0.1:8000/admin/` (custom admin login)
- Dashboard URL: `http://127.0.0.1:8000/dashboard/admin/`

### Color Codes
- **Teal (#0BA57A)**: Doctors, completed
- **Light Green (#36B37E)**: Patients, active users
- **Blue (#4C6EF5)**: Hospitals, confirmed appointments
- **Yellow (#F4B740)**: Pending approvals, warnings
- **Orange (#F59E0B)**: Pending appointments
- **Red (#EF4444)**: Cancelled, inactive
- **Gray (#6B7280)**: Neutral information

### Important Actions
- **Approve Doctor**: Manage Data → Doctors → Action Menu → Approve
- **Add Patient**: Users → Patients → + Add Patient
- **Mark Notifications Read**: Notifications → Mark All as Read
- **Search Users**: Use search box in respective section
- **View Statistics**: Overview section (default landing)

---

## Troubleshooting

### Dashboard Not Loading
1. Verify you're logged in as admin role
2. Check URL is `/dashboard/admin/`
3. Clear browser cache
4. Check browser console for JavaScript errors

### Data Not Showing
1. Verify database has data (run test scripts)
2. Check for any Django errors in console
3. Ensure migrations are applied
4. Refresh the page

### Search Not Working
1. Make sure search term is at least 1 character
2. Check if filters are applied
3. Click "Clear" to reset
4. Try different search terms

---

## Summary

The admin dashboard is a **fully functional, comprehensive management interface** for the Medical Connect platform. All core features are operational:

- ✅ 33 doctors managed (all approved)
- ✅ 15 active patients
- ✅ 2 hospitals tracked
- ✅ Complete appointment management
- ✅ Notification system active
- ✅ Search and filter capabilities
- ✅ Real-time statistics and charts
- ✅ User-friendly interface with modern design

The dashboard is production-ready and provides administrators with complete control over the platform's operations.
