const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendOtp(email, username) {
  const res = await fetch(
    `${BASE_URL}/login?email=${email}&username=${username}`,
    { method: "POST" }
  );
  return res.json();
}

export async function verifyOtp(email, otp) {
  const res = await fetch(
    `${BASE_URL}/verify-otp?email=${email}&otp=${otp}`,
    { method: "POST" }
  );
  return res.json();
}

export async function fetchSlots(date) {
  const res = await fetch(`${BASE_URL}/slots?date=${date}`);
  return res.json();
}

export async function bookSlot(email, slot) {
  return fetch(
    `${BASE_URL}/book?email=${email}&slot=${slot}`,
    { method: "POST" }
  );
}
