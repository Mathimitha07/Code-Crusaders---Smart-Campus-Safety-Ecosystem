from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets
import uuid
import io
import csv
import shutil

import db
from school_rules import validate_qr_session

app = FastAPI(title="Smart Campus Hub (Minimal)")
app.add_middleware(SessionMiddleware, secret_key="CHANGE_ME_TO_SOMETHING_RANDOM")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "od_letters"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def startup():
    db.init_db()


def current_user(request: Request):
    return request.session.get("user")


def require_role(request: Request, role: str):
    u = current_user(request)
    if not u or u.get("role") != role:
        raise HTTPException(status_code=403, detail="Forbidden")
    return u


def utc_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


# -----------------------
# Auth
# -----------------------
@app.get("/")
def root():
    return RedirectResponse("/login", status_code=302)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("auth_login.html", {"request": request})


@app.post("/login")
def login_action(
    request: Request,
    role: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    u = db.get_user(username)
    if not u or u["password"] != password or u["role"] != role:
        return templates.TemplateResponse(
            "auth_login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401,
        )

    request.session["user"] = {
        "role": u["role"],
        "username": u["username"],
        "full_name": u.get("full_name", u["username"]),
    }
    return RedirectResponse(f"/{role}", status_code=302)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)


# -----------------------
# Student Pages
# -----------------------
@app.get("/student")
def student_home(request: Request):
    u = require_role(request, "student")
    marks = db.list_marks_for_student(u["username"])
    od_requests = db.list_od_requests_for_student(u["username"])[:5]
    return templates.TemplateResponse(
        "student_home.html",
        {"request": request, "user": u, "marks": marks[:5], "od_requests": od_requests}
    )


@app.get("/student/attendance")
def student_attendance(request: Request):
    u = require_role(request, "student")
    marks = db.list_marks_for_student(u["username"])
    return templates.TemplateResponse(
        "student_attendance.html",
        {"request": request, "user": u, "marks": marks}
    )


@app.get("/student/attendance/scan")
def student_attendance_scan(request: Request):
    u = require_role(request, "student")
    return templates.TemplateResponse(
        "student_qr_scan.html",
        {"request": request, "user": u}
    )


@app.get("/student/attendance/qr")
def student_attendance_qr(request: Request, sessionId: str, token: str):
    u = require_role(request, "student")
    return templates.TemplateResponse(
        "student_attendance_qr.html",
        {"request": request, "user": u, "sessionId": sessionId, "token": token}
    )


@app.get("/student/safety")
def student_safety(request: Request):
    u = require_role(request, "student")
    return templates.TemplateResponse(
        "student_safety.html",
        {"request": request, "user": u}
    )


@app.get("/student/report")
def student_report(request: Request):
    u = require_role(request, "student")
    return templates.TemplateResponse(
        "student_report.html",
        {"request": request, "user": u}
    )


@app.get("/student/od/request")
def student_od_request_page(request: Request):
    u = require_role(request, "student")
    od_requests = db.list_od_requests_for_student(u["username"])
    return templates.TemplateResponse(
        "student_od_request.html",
        {"request": request, "user": u, "od_requests": od_requests}
    )


# -----------------------
# Admin Pages
# -----------------------
@app.get("/admin")
def admin_home(request: Request):
    u = require_role(request, "admin")
    sessions = db.list_sessions()[:5]
    reports = db.list_reports()[:5]
    od_requests = db.list_od_requests()[:5]
    return templates.TemplateResponse(
        "admin_home.html",
        {
            "request": request,
            "user": u,
            "sessions": sessions,
            "reports": reports,
            "od_requests": od_requests,
        }
    )


@app.get("/admin/attendance/sessions")
def admin_sessions(request: Request):
    u = require_role(request, "admin")
    sessions = db.list_sessions()
    return templates.TemplateResponse(
        "admin_sessions.html",
        {"request": request, "user": u, "sessions": sessions}
    )


@app.get("/admin/attendance/session/{session_id}")
def admin_session_detail(request: Request, session_id: str):
    u = require_role(request, "admin")
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    marks = db.list_marks_for_session(session_id)

    return templates.TemplateResponse(
        "admin_sessions_detail.html",
        {
            "request": request,
            "user": u,
            "sess": sess,
            "marks": marks
        }
    )


@app.post("/admin/attendance/session/{session_id}/manual-mark")
def admin_manual_mark_attendance(
    request: Request,
    session_id: str,
    student_username: str = Form(...),
    student_name: str = Form(...),
    status: str = Form(...),
    reason: str = Form("Manually marked by admin"),
):
    require_role(request, "admin")

    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    if status not in ["PRESENT", "ABSENT", "OD"]:
        raise HTTPException(status_code=400, detail="Invalid attendance status")

    student_username = student_username.strip()
    student_name = student_name.strip()
    reason = reason.strip() or "Manually marked by admin"

    if not student_username or not student_name:
        raise HTTPException(status_code=400, detail="Student username and name are required")

    db.manual_mark_attendance(
        session_id=session_id,
        student_username=student_username,
        student_name=student_name,
        status=status,
        reason=reason,
    )

    return RedirectResponse(f"/admin/attendance/session/{session_id}", status_code=302)


@app.get("/admin/attendance/export/{session_id}")
def export_attendance_csv(request: Request, session_id: str):
    require_role(request, "admin")
    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = db.list_marks_for_session(session_id)

    f = io.StringIO()
    w = csv.writer(f)
    w.writerow(["Class", "SessionId", "Student Name", "Username", "Status", "Reason", "Marked Time"])
    for r in rows:
        w.writerow([
            sess["class_name"],
            session_id,
            r["student_name"],
            r["student_username"],
            r["status"],
            r["reason"],
            r["marked_iso"],
        ])

    f.seek(0)
    filename = f"attendance_{sess['class_name'].replace(' ', '_')}_{session_id[:8]}.csv"
    return StreamingResponse(
        iter([f.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/admin/reports")
def admin_reports(request: Request):
    u = require_role(request, "admin")
    reports = db.list_reports()
    return templates.TemplateResponse(
        "admin_reports.html",
        {"request": request, "user": u, "reports": reports}
    )


@app.get("/admin/od")
def admin_od_requests_page(request: Request):
    u = require_role(request, "admin")
    od_requests = db.list_od_requests()
    return templates.TemplateResponse(
        "admin_od_requests.html",
        {"request": request, "user": u, "od_requests": od_requests}
    )


# -----------------------
# NEW: Automatic Location Capture / Responder View
# -----------------------
@app.get("/admin/emergency-locations")
def admin_emergency_locations(request: Request):
    u = require_role(request, "admin")
    reports = db.list_reports()

    emergency_locations = [
        r for r in reports
        if r["status"] == "EMERGENCY"
        and r.get("lat") is not None
        and r.get("lng") is not None
    ]

    emergency_locations.sort(key=lambda x: x["id"], reverse=True)

    return templates.TemplateResponse(
        "admin_emergency_locations.html",
        {
            "request": request,
            "user": u,
            "locations": emergency_locations,
        }
    )


# -----------------------
# APIs
# -----------------------
@app.post("/api/admin/create-session")
def api_create_session(
    request: Request,
    class_name: str = Form(...),
    start_minutes_from_now: int = Form(0),
    duration_minutes: int = Form(60),
    center_lat: float = Form(...),
    center_lng: float = Form(...),
    radius_m: float = Form(150.0),
):
    require_role(request, "admin")

    now = datetime.now(timezone.utc)
    start = now + timedelta(minutes=start_minutes_from_now)
    end = start + timedelta(minutes=duration_minutes)

    session_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(16)

    db.create_session({
        "id": session_id,
        "class_name": class_name,
        "start_iso": utc_iso(start),
        "end_iso": utc_iso(end),
        "created_iso": utc_iso(now),
        "token": token,
        "center_lat": center_lat,
        "center_lng": center_lng,
        "radius_m": radius_m,
    })

    qr_url = f"/student/attendance/qr?sessionId={session_id}&token={token}"
    return JSONResponse({
        "ok": True,
        "sessionId": session_id,
        "token": token,
        "qrUrl": qr_url
    })


@app.post("/api/student/validate-qr")
async def api_validate_qr(request: Request):
    u = require_role(request, "student")
    body = await request.json()

    session_id = body.get("sessionId")
    token = body.get("token")
    lat = body.get("lat")
    lng = body.get("lng")

    if not session_id or not token or lat is None or lng is None:
        raise HTTPException(status_code=400, detail="Missing fields")

    sess = db.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    user_row = db.get_user(u["username"])
    student_name = (user_row.get("full_name") or u["username"]) if user_row else u["username"]

    today_str = datetime.now().date().isoformat()
    approved_od = db.get_approved_od_for_student_on_date(u["username"], today_str)

    if approved_od:
        status = "OD"
        reason = f"Approved OD - {approved_od['event_name']} ({approved_od['event_type']})"
    else:
        status, reason = validate_qr_session(sess, token, float(lat), float(lng))

    db.mark_attendance(session_id, u["username"], student_name, status, reason)

    return JSONResponse({
        "ok": True,
        "status": status,
        "reason": reason,
        "class_name": sess["class_name"]
    })


@app.post("/api/student/report")
async def api_report(request: Request):
    u = require_role(request, "student")
    body = await request.json()
    title = (body.get("title") or "").strip()
    details = (body.get("details") or "").strip()

    if not title or not details:
        raise HTTPException(status_code=400, detail="Title and details required")

    payload = {
        "student_username": u["username"],
        "title": title,
        "details": details,
        "lat": body.get("lat"),
        "lng": body.get("lng"),
        "created_iso": datetime.now(timezone.utc).isoformat(),
        "status": "NEW"
    }
    db.create_report(payload)
    return JSONResponse({"ok": True})


# -----------------------
# OD REQUEST
# -----------------------
@app.post("/student/od/request")
async def submit_od_request(
    request: Request,
    college_name: str = Form(...),
    event_type: str = Form(...),
    event_name: str = Form(...),
    event_date: str = Form(...),
    parent_letter: UploadFile = File(...),
    clg_od_letter: UploadFile = File(...),
):
    u = require_role(request, "student")

    if event_type not in ["Intercollege", "Intracollege"]:
        raise HTTPException(status_code=400, detail="Invalid event type")

    timestamp = int(datetime.now().timestamp())

    parent_safe = f"{u['username']}_{timestamp}_{parent_letter.filename}"
    parent_path = UPLOAD_DIR / parent_safe
    with parent_path.open("wb") as buffer:
        shutil.copyfileobj(parent_letter.file, buffer)

    clg_safe = f"{u['username']}_{timestamp}_{clg_od_letter.filename}"
    clg_path = UPLOAD_DIR / clg_safe
    with clg_path.open("wb") as buffer:
        shutil.copyfileobj(clg_od_letter.file, buffer)

    user_row = db.get_user(u["username"])
    student_name = (user_row.get("full_name") or u["username"]) if user_row else u["username"]

    db.create_od_request({
        "student_username": u["username"],
        "student_name": student_name,
        "college_name": college_name.strip(),
        "event_type": event_type.strip(),
        "event_name": event_name.strip(),
        "event_date": event_date.strip(),
        "parent_letter_path": f"/static/uploads/od_letters/{parent_safe}",
        "clg_od_letter_path": f"/static/uploads/od_letters/{clg_safe}",
        "status": "PENDING",
        "created_iso": datetime.now(timezone.utc).isoformat(),
        "reviewed_iso": None,
    })

    return RedirectResponse("/student/od/request", status_code=302)


# -----------------------
# VOICE / EMERGENCY ALERT SYSTEM
# -----------------------
@app.post("/api/student/emergency")
async def emergency_alert(request: Request):
    u = require_role(request, "student")
    body = await request.json()

    payload = {
        "student_username": u["username"],
        "title": "VOICE EMERGENCY ALERT",
        "details": "Voice command triggered emergency alert",
        "lat": body.get("lat"),
        "lng": body.get("lng"),
        "created_iso": datetime.now(timezone.utc).isoformat(),
        "status": "EMERGENCY",
    }

    db.create_report(payload)

    return JSONResponse({"ok": True})


@app.get("/api/admin/check-emergency")
def check_emergency(request: Request):
    require_role(request, "admin")

    alerts = db.list_reports()

    emergencies = [
        a for a in alerts
        if a["status"] == "EMERGENCY"
    ]

    emergencies.sort(key=lambda x: x["id"], reverse=True)

    return {"alerts": emergencies}


# -----------------------
# NEW: Automatic Location Capture API
# -----------------------
@app.get("/api/admin/emergency-locations")
def api_admin_emergency_locations(request: Request):
    require_role(request, "admin")

    reports = db.list_reports()

    locations = [
        {
            "id": r["id"],
            "student_username": r["student_username"],
            "title": r["title"],
            "details": r["details"],
            "lat": r["lat"],
            "lng": r["lng"],
            "created_iso": r["created_iso"],
            "status": r["status"],
        }
        for r in reports
        if r["status"] == "EMERGENCY"
        and r.get("lat") is not None
        and r.get("lng") is not None
    ]

    locations.sort(key=lambda x: x["id"], reverse=True)

    return JSONResponse({"locations": locations})


@app.post("/admin/od/{od_id}/approve")
def approve_od(request: Request, od_id: int):
    require_role(request, "admin")
    db.update_od_status(od_id, "APPROVED")
    return RedirectResponse("/admin/od", status_code=302)


@app.post("/admin/od/{od_id}/reject")
def reject_od(request: Request, od_id: int):
    require_role(request, "admin")
    db.update_od_status(od_id, "REJECTED")
    return RedirectResponse("/admin/od", status_code=302)