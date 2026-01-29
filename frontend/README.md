---

# 📗 `frontend/README.md`

```md
# ServeQ Frontend – Queue & Appointment Manager

This is the frontend web application for **ServeQ**, a mobile-first queue and appointment management prototype.

The application allows users to:
- Log in using OTP
- View date-based time slots
- Book an appointment
- Track queue status in real time
- Receive in-app reminders

---

## Tech Stack

- React
- Vite
- JavaScript
- CSS (mobile-first design)

---

## Features

- Email-based OTP login (in-app OTP for demo)
- 7-day date selector
- Time slots from **9:00 AM to 5:00 PM**
- Slot booking confirmation
- Real-time queue simulation
- In-app appointment reminders

---

## Application Flow

1. User enters email
2. OTP is generated and shown in-app
3. User verifies OTP
4. User selects a date (within next 7 days)
5. Available time slots are fetched from backend
6. User books a slot
7. Queue status is displayed with live updates

---

## Project Structure

src/
├── pages/
│ ├── Login.jsx
│ ├── OtpVerify.jsx
│ ├── Slots.jsx
│ └── Queue.jsx
├── services/
│ └── api.js
├── App.jsx
├── main.jsx
└── index.css


---

## How to Run

### 1. Install dependencies
```bash
npm install
```
### 2. Start development server

```bash
npm run dev
```

### Application runs at:

http://localhost:5173