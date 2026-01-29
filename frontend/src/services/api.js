const BASE_URL =
  import.meta.env.VITE_API_URL ||
  window.location.origin;

export const sendOtp = async (email, username) => {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, username }),
  });

  if (!res.ok) {
    throw new Error("OTP generation failed");
  }

  return res.json();
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
