from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timezone

def haversine_m(lat1, lon1, lat2, lon2) -> float:
    # Earth radius (m)
    R = 6371000.0
    p1 = radians(lat1); p2 = radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(p1)*cos(p2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def parse_iso(s: str) -> datetime:
    # stored as UTC ISO
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def validate_qr_session(session: dict, token: str, student_lat: float, student_lng: float):
    """
    Rules:
    - token must match
    - valid for 60 seconds from created_iso
    - must be within start/end window
    - must be inside geofence radius
    """
    if token != session["token"]:
        return ("ABSENT", "Invalid QR token")

    created = parse_iso(session["created_iso"])
    start = parse_iso(session["start_iso"])
    end = parse_iso(session["end_iso"])
    now = now_utc()

    # 1-minute validity
    if (now - created).total_seconds() > 60:
        return ("ABSENT", "QR expired (valid only 1 minute)")

    # class time window
    if not (start <= now <= end):
        return ("ABSENT", "Outside class time window")

    # geofence
    dist = haversine_m(student_lat, student_lng, session["center_lat"], session["center_lng"])
    if dist > session["radius_m"]:
        return ("ABSENT", f"Outside geofence ({int(dist)}m > {int(session['radius_m'])}m)")

    return ("PRESENT", "Valid scan inside geofence and time window")