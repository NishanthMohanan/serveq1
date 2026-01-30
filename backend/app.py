from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pathlib import Path
from datetime import datetime, timedelta
import json, uuid, time, random
import pytz
import os
import logging
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

app = FastAPI(title="ServeQ Backend", version="1.0.0")

# CORS configuration - Frontend and backend on same Render service
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

logger.info(f"Configured CORS origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# Global exception handlers for proper error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "Invalid request data",
            "errors": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": "Internal server error"
        }
    )


IST = pytz.timezone("Asia/Kolkata")

# Initialize data directory
DATA_DIR = Path("data")
try:
    DATA_DIR.mkdir(exist_ok=True)
    logger.info(f"Data directory ready: {DATA_DIR.resolve()}")
except Exception as e:
    logger.error(f"Failed to create data directory: {e}")
    raise

USERS_FILE = DATA_DIR / "users.json"
BOOKINGS_FILE = DATA_DIR / "bookings.json"
NOTIFICATIONS_FILE = DATA_DIR / "notifications.json"
SLOTS_FILE = DATA_DIR / "slots.json"

OTP_STORE = {}

# Static file serving configuration
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "static"

logger.info(f"Frontend directory configured: {FRONTEND_DIR}")

# Startup event to validate environment and initialize files
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated")
    
    # Validate data files exist or create them
    files_to_check = [
        (USERS_FILE, []),
        (BOOKINGS_FILE, []),
        (NOTIFICATIONS_FILE, []),
        (SLOTS_FILE, {"working_hours": {"start": "09:00", "end": "17:00", "interval_minutes": 30}})
    ]
    
    for file_path, default in files_to_check:
        if not file_path.exists():
            try:
                with open(file_path, "w") as f:
                    json.dump(default, f, indent=2)
                logger.info(f"Created data file: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to create {file_path.name}: {e}")
                raise
    
    # Verify frontend files
    if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
        logger.info(f"Frontend files verified at {FRONTEND_DIR}")
    else:
        logger.warning(f"Frontend files not found at {FRONTEND_DIR}")
    
    logger.info("Application startup completed successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")

# ---------------- HELPERS ---------------- #

def read_json(file, default):
    try:
        if not file.exists():
            logger.debug(f"File not found, returning default: {file.name}")
            return default
        with open(file, "r") as f:
            data = json.load(f)
            logger.debug(f"Successfully read {file.name}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file.name}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error reading {file.name}: {e}")
        return default

def write_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Successfully wrote to {file.name}")
    except Exception as e:
        logger.error(f"Failed to write {file.name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save data"
        )

def now_ist():
    return datetime.now(IST)

# ---------------- AUTH ENDPOINTS ---------------- #

@app.post("/api/login")
def login(data: LoginRequest):
    email = data.email
    username = data.username
    
    logger.info(f"Login attempt for email: {email}")
    
    if not email or not username:
        logger.warning(f"Login failed: missing email or username")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing email or username"
        )
    
    try:
        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = {
            "otp": otp,
            "expires_at": time.time() + 300,
            "username": username
        }
        logger.info(f"OTP generated for {email}")
        return {"success": True, "otp": otp}
    except Exception as e:
        logger.error(f"Login error for {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.post("/api/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    email = data.email
    otp = data.otp
    
    logger.info(f"OTP verification attempt for email: {email}")
    
    if not email or not otp:
        logger.warning(f"OTP verification failed: missing email or otp")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing email or otp"
        )
    
    try:
        record = OTP_STORE.get(email)
        if not record:
            logger.warning(f"OTP verification failed for {email}: no OTP found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No OTP found for this email"
            )
        
        if record["otp"] != otp:
            logger.warning(f"OTP verification failed for {email}: incorrect OTP")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        if time.time() > record["expires_at"]:
            logger.warning(f"OTP verification failed for {email}: OTP expired")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired"
            )

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
            logger.info(f"New user created: {email}")
        else:
            user["last_login"] = now
            logger.info(f"User login: {email}")

        write_json(USERS_FILE, users)
        OTP_STORE.pop(email, None)

        logger.info(f"OTP verification successful for {email}")
        return {"success": True, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OTP verification error for {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )

# ---------------- SLOTS ENDPOINTS ---------------- #

@app.get("/api/slots")
def get_slots(date: str):
    logger.info(f"Slots requested for date: {date}")
    
    try:
        slots_data = read_json(SLOTS_FILE, {})
        config = slots_data.get("working_hours")
        if not config:
            logger.error("Slot configuration missing from slots.json")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Slot configuration missing"
            )
        
        start_h, start_m = map(int, config["start"].split(":"))
        end_h, end_m = map(int, config["end"].split(":"))
        interval = config["interval_minutes"]

        bookings = read_json(BOOKINGS_FILE, [])
        booked_starts = {b["slot_start"] for b in bookings if b["status"] == "ACTIVE"}

        try:
            selected = IST.localize(datetime.strptime(date, "%Y-%m-%d"))
        except ValueError as e:
            logger.warning(f"Invalid date format: {date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format, expected YYYY-MM-DD"
            )
        
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

        logger.info(f"Slots retrieved for {date}: {len(slots)} slots total")
        return {"slots": slots}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching slots for {date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch slots"
        )

# ---------------- BOOKINGS ENDPOINTS ---------------- #

@app.post("/api/book")
def book_slot(data: BookSlotRequest):
    email = data.email
    slot = data.slot
    
    logger.info(f"Booking request from {email} for slot: {slot}")
    
    if not email or not slot:
        logger.warning(f"Booking failed: missing email or slot")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing email or slot"
        )

    try:
        bookings = read_json(BOOKINGS_FILE, [])

        # Check for one active booking per user
        if any(b for b in bookings if b["email"] == email and b["status"] == "ACTIVE"):
            logger.warning(f"Booking failed for {email}: already has active booking")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has an active booking"
            )

        try:
            date_part, time_part = slot.split(" ", 1)
            start_str, end_str = [s.strip() for s in time_part.split("-")]
        except Exception:
            logger.warning(f"Booking failed: invalid slot format: {slot}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid slot format, expected 'YYYY-MM-DD HH:MM AM/PM-HH:MM AM/PM'"
            )

        try:
            start_dt = IST.localize(datetime.strptime(
                f"{date_part} {start_str}", "%Y-%m-%d %I:%M %p"
            ))
            end_dt = IST.localize(datetime.strptime(
                f"{date_part} {end_str}", "%Y-%m-%d %I:%M %p"
            ))
        except Exception:
            logger.warning(f"Booking failed: invalid date/time format in slot: {slot}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date/time in slot"
            )

        if start_dt <= now_ist():
            logger.warning(f"Booking failed for {email}: attempting to book past slot")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book past slot"
            )

        if any(b for b in bookings if b["slot_start"] == start_dt.isoformat()):
            logger.warning(f"Booking failed: slot already booked: {start_dt.isoformat()}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot already booked"
            )

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

        logger.info(f"Booking successful for {email}: {booking['id']}")
        return {"success": True, "message": "Booked successfully", "booking": booking}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Booking error for {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book slot"
        )

# ---------------- NOTIFICATIONS ENDPOINTS ---------------- #

@app.get("/api/notifications")
def get_notifications(email: str):
    logger.info(f"Notifications requested for {email}")
    
    try:
        if not email:
            logger.warning("Notifications request without email")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email required"
            )
        
        bookings = read_json(BOOKINGS_FILE, [])
        notifications = read_json(NOTIFICATIONS_FILE, [])

        # Generate reminders for active bookings within 10 minutes
        for b in bookings:
            if b["email"] != email or b["status"] != "ACTIVE":
                continue

            try:
                start = datetime.fromisoformat(b["slot_start"])
            except Exception as e:
                logger.warning(f"Failed to parse slot time for booking {b.get('id')}: {e}")
                continue

            time_until = (start - now_ist()).total_seconds()
            if 0 <= time_until <= 600:  # Within 10 minutes
                # Check if reminder already exists
                if not any(
                    n for n in notifications
                    if n["email"] == email and n["type"] == "REMINDER" and not n["cleared"]
                ):
                    reminder = {
                        "id": str(uuid.uuid4()),
                        "email": email,
                        "message": "Your appointment is in 10 minutes",
                        "type": "REMINDER",
                        "created_at": now_ist().isoformat(),
                        "cleared": False
                    }
                    notifications.append(reminder)
                    logger.info(f"Reminder created for {email}")

        write_json(NOTIFICATIONS_FILE, notifications)

        user_notifications = [
            n for n in notifications
            if n["email"] == email and not n["cleared"]
        ]
        
        logger.info(f"Retrieved {len(user_notifications)} notifications for {email}")
        return user_notifications
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications for {email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )

@app.post("/api/notifications/clear")
def clear_notification(notification_id: str):
    logger.info(f"Clear notification request for: {notification_id}")
    
    if not notification_id:
        logger.warning("Clear notification without notification_id")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification ID required"
        )
    
    try:
        notifications = read_json(NOTIFICATIONS_FILE, [])
        found = False
        
        for n in notifications:
            if n["id"] == notification_id:
                n["cleared"] = True
                found = True
                logger.info(f"Notification cleared: {notification_id}")
                break
        
        if not found:
            logger.warning(f"Notification not found: {notification_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        write_json(NOTIFICATIONS_FILE, notifications)
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing notification {notification_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear notification"
        )

# ---------------- SPA ROUTES (serve frontend) ---------------- #

# Health check endpoint for Render
@app.get("/health", include_in_schema=True)
def health_check():
    """Return basic health status and check critical files."""
    try:
        data_files = {f.name: f.exists() for f in [USERS_FILE, BOOKINGS_FILE, NOTIFICATIONS_FILE, SLOTS_FILE]}
        static_ok = FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists()
        return {
            "success": True,
            "uptime": True,
            "data_files": data_files,
            "static": static_ok
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Health check failed")

# Serve the main SPA entry point
@app.get("/", tags=["SPA"], include_in_schema=False)
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        logger.debug("Serving index.html from root")
        return FileResponse(index_file, media_type="text/html")
    logger.error(f"index.html not found at {index_file}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Frontend not available"
    )

# Catch-all for SPA routing - serve files or index.html
@app.get("/{path:path}", tags=["SPA"], include_in_schema=False)
def serve_spa(path: str):
    # Skip API routes - let them be handled by FastAPI
    if path.startswith("api/"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    file_path = FRONTEND_DIR / path
    
    # If the requested file exists, serve it
    if file_path.exists() and file_path.is_file():
        logger.debug(f"Serving file: {path}")
        return FileResponse(file_path)
    
    # Otherwise, serve index.html for SPA routing
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        logger.debug(f"SPA route not found ({path}), serving index.html")
        return FileResponse(index_file, media_type="text/html")
    
    logger.error(f"Neither file {path} nor index.html found")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
