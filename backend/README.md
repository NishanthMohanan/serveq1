# ServeQ Backend – Queue & Appointment Manager

This is the backend service for **ServeQ**, a queue and appointment management prototype.
It is built using **FastAPI** and uses **JSON files** for data storage instead of a database.

---

## Features

- OTP-based user authentication (in-app OTP for demo)
- Date-based slot generation
- Working hours: **9:00 AM – 5:00 PM**
- Slot interval: **30 minutes**
- Slot booking API
- No database dependency (JSON-based storage)

---

## Tech Stack

- Python
- FastAPI
- Uvicorn

---

## Project Structure

backend/
├── app.py
├── data/
│ ├── slots.json
│ └── bookings.json
└── requirements.txt


---

## Authentication Flow

1. User provides email
2. Backend generates a 6-digit OTP
3. OTP is returned in the API response (demo purpose)
4. User submits OTP for verification
5. Successful verification allows access to slots

> Note: OTP is displayed in-app for prototype/demo purposes.  
> No email or SMS service is used.

---

## Slot Management

- Slots are generated dynamically based on:
  - Selected date
  - Working hours defined in `slots.json`
- Next **7 days** are supported
- No hardcoded slots

---

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server

```
bash
uvicorn app:app --reload

```
Server runs at:
ardino
http://localhost:8000