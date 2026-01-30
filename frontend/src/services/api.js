const BASE_URL =
  import.meta.env.MODE === "development"
    ? "http://localhost:8000"
    : "/api";

export const sendOtp = async (email, username) => {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, username }),
  });

  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error);
  return data;
};


export async function verifyOtp(email, otp) {
  const res = await fetch(`${BASE_URL}/verify-otp`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, otp }),
  });

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
  const res = await fetch(`${BASE_URL}/book`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, slot }),
  });

  const data = await res.json();
  if (!res.ok || data.error) {
    throw new Error(data.error || "Failed to book slot");
  }
  return data;
}
