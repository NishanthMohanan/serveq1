const BASE_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : "http://localhost:8000");

export async function sendOtp(email, username) {
  const res = await fetch(
    `${BASE_URL}/login?email=${email}&username=${username}`,
    { method: "POST" }
  );
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || "Failed to generate OTP");
  }
  return data;
}

export async function verifyOtp(email, otp) {
  const res = await fetch(
    `${BASE_URL}/verify-otp?email=${email}&otp=${otp}`,
    { method: "POST" }
  );
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || "Failed to verify OTP");
  }
  return data;
}

export async function fetchSlots(date) {
  const res = await fetch(`${BASE_URL}/slots?date=${date}`);
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || "Failed to fetch slots");
  }
  return data;
}

export async function bookSlot(email, slot) {
  const res = await fetch(
    `${BASE_URL}/book?email=${email}&slot=${slot}`,
    { method: "POST" }
  );
  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || "Failed to book slot");
  }
  return data;
}
