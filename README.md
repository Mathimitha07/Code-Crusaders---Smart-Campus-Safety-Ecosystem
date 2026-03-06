### Smart Campus Hub

Smart Campus Hub is a modern campus management system that combines QR-based attendance, geolocation validation, emergency alerts, and safety reporting into a single platform for students and administrators.

The system improves attendance accuracy, campus safety, and emergency response using simple web technologies.

### Features
QR Code Attendance

Admin creates attendance sessions.

System generates a QR code.

Students scan the QR code using their phone.

Attendance is recorded automatically.

### Geolocation Validation

Student location is captured during QR scan.

Attendance is allowed only within campus geofence.

Prevents proxy attendance.

### Manual Attendance (Admin)

Admins can manually mark attendance if QR fails.

Available options:

PRESENT

ABSENT

OD

### On Duty Request System

Students can submit OD requests including:

College name

Event name

Event type

Event date

Parent letter upload

College permission letter upload

Admins can:

Approve

Reject

Approved OD automatically marks attendance as OD.

### Student Safety Reporting

Students can report campus incidents by submitting:

Title

Description

Current location

Admins can review reports from the dashboard.

### Voice-Based Emergency Alert

Students can trigger emergency alerts using voice commands such as:

HELP
EMERGENCY
SAVE ME

The system:

Detects voice commands

Sends alert to server

Notifies admin dashboard

Admin receives:

Alarm sound

Emergency popup alert

### Automatic Location Capture

When an emergency alert is triggered:

Student GPS coordinates are captured.

Location is stored in the database.

Admin can open location in Google Maps.

### System Architecture
Student Device
      │
      │ QR Scan / Voice Alert / Report
      ▼
FastAPI Backend
      │
      ├── Attendance System
      ├── Emergency Alert System
      ├── OD Management System
      └── Safety Reporting
      │
      ▼
SQLite Database
      │
      ▼
Admin Dashboard
      │
      ├── Attendance Management
      ├── Emergency Alerts
      ├── Safety Reports
      └── Location Tracking

### Tech Stack
Backend

Python

FastAPI

SQLite

Frontend

HTML

Tailwind CSS

JavaScript

Jinja2 Templates

APIs Used

Browser Geolocation API

Web Speech API (Voice Detection)

Tools

Uvicorn

Ngrok (for external testing)

### Project Structure
FINAL/
│
├── __pycache__/
│
├── backend/
│   │
│   ├── static/
│   │   │
│   │   ├── uploads/
│   │   │
│   │   ├── alarm.mp3
│   │   ├── app.js
│   │   ├── manifest.json
│   │   ├── offline.js
│   │   ├── pwa.js
│   │   ├── style.css
│   │   └── sw.js
│   │
│   ├── templates/
│   │   │
│   │   ├── admin_emergency_locations.html
│   │   ├── admin_home.html
│   │   ├── admin_od_requests.html
│   │   ├── admin_reports.html
│   │   ├── admin_sessions_detail.html
│   │   ├── admin_sessions.html
│   │   ├── auth_login.html
│   │   ├── layout.html
│   │   ├── student_attendance_qr.html
│   │   ├── student_attendance_scan.html
│   │   ├── student_attendance.html
│   │   ├── student_home.html
│   │   ├── student_od_request.html
│   │   ├── student_qr_scan.html
│   │   ├── student_report.html
│   │   └── student_safety.html
│   │
│   ├── venv/
│   │
│   ├── db.py
│   ├── db.sqlite
│   ├── main.py
│   ├── ngrok.exe
│   ├── requirements.txt
│   └── school_rules.py
│
└── venv/


### Installation
1️. Clone the repository

    git clone https://github.com/yourusername/smart-campus-hub.git
    cd smart-campus-hub/backend


2️. Create virtual environment
      python -m venv venv

  Activate environment:

      Windows:
      venv\Scripts\activate


3. Install dependencies
      pip install fastapi uvicorn jinja2 python-multipart

5. Run the server
      uvicorn main:app --reload

6. Server will start at:
    http://127.0.0.1:8000

### Demo Login
Admin
Role: admin
Username: admin
Password: 12345

Student
Role: student
Username: student1
Password: 12345

### Credentials may vary depending on database setup.

### Demo Flow

1️. Admin creates attendance session
2️. Student scans QR and marks attendance
3️. Student submits OD request
4️. Admin approves OD
5️. Student triggers emergency voice alert
6️. Admin receives emergency alarm
7️. Admin checks emergency location

### Advantages

1. Prevents proxy attendance

2. Faster emergency response

3. Digital OD management

4. Real-time alerts

5. Easy admin monitoring


### Future Improvements

        Mobile app integration

        WebSocket real-time alerts

        AI-based behavior detection

        Campus heatmap analysis

        Facial recognition attendance


        
