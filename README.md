# 🎓 Smart Campus Hub

**Smart Campus Hub** is a web-based campus management system designed to improve **attendance monitoring and campus safety** using modern technologies like **QR-based attendance, geolocation verification, and voice-triggered emergency alerts**.

The system provides two roles:

* 👨‍🎓 **Student**
* 👨‍🏫 **Admin**

It integrates **attendance automation, safety reporting, OD request management, and emergency alerting** into a single platform.

---

# 🚀 Key Features

## 📷 QR-Based Attendance

* Admin creates attendance sessions.
* System generates a QR code.
* Students scan the QR code using their phone.
* Attendance is automatically recorded.

---

## 📍 Location-Based Validation

* Student GPS location is captured during QR scan.
* Attendance is allowed only inside the **campus geofence**.
* Prevents proxy attendance.

---

## 📝 Manual Attendance (Admin)

Admins can manually mark attendance if QR scanning fails.

Available status:

* **PRESENT**
* **ABSENT**
* **OD (On Duty)**

---

## 📄 OD Request System

Students can submit On-Duty requests with:

* Event details
* Parent permission letter
* College permission letter

Admins can:

* Approve
* Reject

Approved OD automatically marks attendance as **OD**.

---

## 🛡 Student Safety Reporting

Students can report campus incidents including:

* Incident title
* Description
* Current location

Admins can view and manage reports from the dashboard.

---

## 🚨 Voice-Based Emergency Alert

Students can trigger emergency alerts using voice commands like:

```
HELP
EMERGENCY
SAVE ME
```

The system will:

* Capture microphone input
* Send emergency alert to server
* Notify the admin dashboard

Admin receives:

* 🔊 Alarm sound
* 🚨 Popup alert

---

## 📍 Automatic Location Capture

When an emergency alert is triggered:

* Student GPS coordinates are captured
* Stored in database
* Admin can open location directly in **Google Maps**

---

# 🧠 System Architecture

```
Student Device
   │
   │ QR Scan / Voice Alert / Incident Report
   ▼
FastAPI Backend
   │
   ├── Attendance Engine
   ├── Emergency Alert System
   ├── OD Management
   └── Safety Reporting
   │
   ▼
SQLite Database
   │
   ▼
Admin Dashboard
   │
   ├── Attendance Monitoring
   ├── Emergency Alerts
   ├── Safety Reports
   └── Location Tracking
```

---

# 🛠 Tech Stack

### Backend

* **Python**
* **FastAPI**
* **SQLite**

### Frontend

* **HTML**
* **Tailwind CSS**
* **JavaScript**
* **Jinja2 Templates**

### APIs

* Browser **Geolocation API**
* **Web Speech API** (Voice detection)

### Tools

* **Uvicorn**
* **Ngrok** (for external testing)

---

# 📂 Project Structure

```
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
```

---

# ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/smart-campus-hub.git
cd smart-campus-hub/backend
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

Windows:

```
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```
pip install fastapi uvicorn jinja2 python-multipart
```

Or install from requirements file:

```
pip install -r requirements.txt
```

---

### 4️⃣ Run the Server

```
uvicorn main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

---

# 👤 Demo Login

### Admin

```
Role: admin
Username: admin
Password: admin
```

### Student

```
Role: student
Username: student1
Password: student
```

*(Credentials depend on database configuration.)*

---

# 🧪 Demo Flow

1️⃣ Admin creates attendance session
2️⃣ Student scans QR and marks attendance
3️⃣ Student submits OD request
4️⃣ Admin approves OD
5️⃣ Student triggers emergency voice alert
6️⃣ Admin receives emergency alarm
7️⃣ Admin views student location

---

# 🌟 Advantages

* Prevents proxy attendance
* Real-time emergency alerts
* Digital OD approval system
* Automatic location capture
* Centralized campus monitoring

---

# 🔮 Future Enhancements

* Mobile application integration
* WebSocket real-time alerts
* AI-based safety detection
* Campus heatmap analytics
* Face recognition attendance


