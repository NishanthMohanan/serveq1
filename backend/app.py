from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timedelta
from pathlib import Path
import json, uuid, time, random
import pytz
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    username: str
class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class BookSlotRequest(BaseModel):
    email: str
    slot: str



# ---------------- APP SETUP ---------------- #

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

IST = pytz.timezone("Asia/Kolkata")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
SLOTS_FILE = DATA_DIR / "slots.json"

OTP_STORE = {}  

# ---------------- HELPERS ---------------- #

def read_json(file, default):
    if not file.exists():
        return default
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def write_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def now_ist():
    return datetime.now(IST)

# ---------------- AUTH ---------------- #

@app.post("/api/login")
def login(data: LoginRequest):
    email = data.email
    username = data.username
    if not email or not username:
        return {"error": "Missing email or username"}
    
    try:
        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = {
            "otp": otp,
            "expires_at": time.time() + 300,
            "username": username
        }
        return {"otp": otp, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    email = data.email
    otp = data.otp
    if not email or not otp:
        return {"success": False, "error": "Missing email or otp"}
    
    try:
        record = OTP_STORE.get(email)
        if not record:
            return {"success": False, "error": "No OTP found for this email"}
        if record["otp"] != otp:
            return {"success": False, "error": "Invalid OTP"}
        if time.time() > record["expires_at"]:
            return {"success": False, "error": "OTP expired"}

        users = read_json(USERS_FILE, [])
        user = next((u for u in users if u["email"] == email), None)

        now = now_ist().isoformat()

        if not user:
            user = {
                "id": str(uuid.uuid4()),
                "email": email,
                "username": record["username"],
                "created_at": now,
                "last_login": now
            }
            users.append(user)
        else:
            user["last_login"] = now

        write_json(USERS_FILE, users)
        OTP_STORE.pop(email, None)

        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------- SLOTS ---------------- #

@app.get("/api/slots")
def get_slots(date: str):
    slots_data = read_json(SLOTS_FILE, {})
    config = slots_data.get("working_hours")
    if not config:
        return {"error": "Slot configuration missing"}
    start_h, start_m = map(int, config["start"].split(":"))
    end_h, end_m = map(int, config["end"].split(":"))
    interval = config["interval_minutes"]

    bookings = read_json(BOOKINGS_FILE, [])
    booked_starts = {b["slot_start"] for b in bookings if b["status"] == "ACTIVE"}

    selected = IST.localize(datetime.strptime(date, "%Y-%m-%d"))
    current = selected.replace(hour=start_h, minute=start_m, second=0)
    end = selected.replace(hour=end_h, minute=end_m, second=0)

    slots = []

    while current < end:
        next_time = current + timedelta(minutes=interval)
        start_iso = current.isoformat()

        slots.append({
            "start": current.strftime("%I:%M %p"),
            "end": next_time.strftime("%I:%M %p"),
            "is_bookable": current > now_ist() and start_iso not in booked_starts,
            "is_booked": start_iso in booked_starts
        })

        current = next_time

    return {"slots": slots}

# ---------------- BOOKINGS ---------------- #

@app.post("/api/book")
def book_slot(data: BookSlotRequest):
    email = data.email
    slot = data.slot
    bookings = read_json(BOOKINGS_FILE, [])

    # one active booking per user
    if any(b for b in bookings if b["email"] == email and b["status"] == "ACTIVE"):
        return {"error": "User already has an active booking"}

    date_part, time_part = slot.split(" ", 1)
    start_str, end_str = time_part.split("-")

    start_dt = IST.localize(datetime.strptime(
        f"{date_part} {start_str}", "%Y-%m-%d %I:%M %p"
    ))
    end_dt = IST.localize(datetime.strptime(
        f"{date_part} {end_str}", "%Y-%m-%d %I:%M %p"
    ))

    if start_dt <= now_ist():
        return {"error": "Cannot book past slot"}

    if any(b for b in bookings if b["slot_start"] == start_dt.isoformat()):
        return {"error": "Slot already booked"}

    booking = {
        "id": str(uuid.uuid4()),
        "email": email,
        "slot_start": start_dt.isoformat(),
        "slot_end": end_dt.isoformat(),
        "status": "ACTIVE"
    }

    bookings.append(booking)
    write_json(BOOKINGS_FILE, bookings)

    notifications = read_json(NOTIFICATIONS_FILE, [])
    notifications.append({
        "id": str(uuid.uuid4()),
        "email": email,
        "message": f"Booking confirmed for {start_str}",
        "type": "CONFIRMATION",
        "created_at": now_ist().isoformat(),
        "cleared": False
    })
    write_json(NOTIFICATIONS_FILE, notifications)

    return {"message": "Booked successfully"}

# ---------------- NOTIFICATIONS ---------------- #

@app.get("/api/notifications")
def get_notifications(email: str):
    bookings = read_json(BOOKINGS_FILE, [])
    notifications = read_json(NOTIFICATIONS_FILE, [])

    # reminder generation
    for b in bookings:
        if b["email"] != email or b["status"] != "ACTIVE":
            continue

        start = datetime.fromisoformat(b["slot_start"])
        if 0 <= (start - now_ist()).total_seconds() <= 600:
            if not any(
                n for n in notifications
                if n["email"] == email and n["type"] == "REMINDER" and not n["cleared"]
            ):
                notifications.append({
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "message": "Your appointment is in 10 minutes",
                    "type": "REMINDER",
                    "created_at": now_ist().isoformat(),
                    "cleared": False
                })

    write_json(NOTIFICATIONS_FILE, notifications)

    return [
        n for n in notifications
        if n["email"] == email and not n["cleared"]
    ]

@app.post("/api/notifications/clear")
def clear_notification(notification_id: str):
    notifications = read_json(NOTIFICATIONS_FILE, [])
    for n in notifications:
        if n["id"] == notification_id:
            n["cleared"] = True
    write_json(NOTIFICATIONS_FILE, notifications)
    return {"success": True}

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "static"

# Serve assets (JS, CSS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Serve React app
@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/{path:path}")
def serve_spa(path: str):
    return FileResponse(FRONTEND_DIR / "index.html")