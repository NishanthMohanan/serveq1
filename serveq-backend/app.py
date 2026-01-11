from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import json
import time
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OTP_STORE = {}

# ---------------- OTP LOGIN ---------------- #

@app.post("/login")
def login(email: str):
    otp = str(random.randint(100000, 999999))
    OTP_STORE[email] = otp

    return {
        "message": "OTP generated",
        "otp": otp  # 👈 exposed for demo
    }

@app.post("/verify-otp")
def verify_otp(email: str, otp: str):
    if OTP_STORE.get(email) == otp:
        return {"success": True}
    return {"success": False}

# ---------------- SLOTS ---------------- #

@app.get("/slots")
def get_slots(date: str):
    with open("data/slots.json") as f:
        config = json.load(f)["working_hours"]

    start_hour, start_min = map(int, config["start"].split(":"))
    end_hour, end_min = map(int, config["end"].split(":"))
    interval = config["interval_minutes"]

    selected_date = datetime.strptime(date, "%Y-%m-%d")

    slots = []
    current = selected_date.replace(
        hour=start_hour,
        minute=start_min,
        second=0
    )

    end_time = selected_date.replace(
        hour=end_hour,
        minute=end_min,
        second=0
    )

    while current < end_time:
        next_time = current + timedelta(minutes=interval)
        slots.append({
            "start": current.strftime("%I:%M %p"),
            "end": next_time.strftime("%I:%M %p")
        })
        current = next_time

    return {
        "date": date,
        "slots": slots
    }

# ---------------- BOOKING ---------------- #

@app.post("/book")
def book_slot(email: str, slot: str):
    with open("data/bookings.json", "r+") as f:
        data = json.load(f)
        data.append({
            "email": email,
            "slot": slot,
            "timestamp": time.time()
        })
        f.seek(0)
        json.dump(data, f, indent=2)

    return {"message": "Slot booked successfully"}
