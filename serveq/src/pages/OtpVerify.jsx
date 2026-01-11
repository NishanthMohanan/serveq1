import { useState } from "react";
import { verifyOtp } from "../services/api";

export default function OtpVerify({ email, onSuccess }) {
  const [otp, setOtp] = useState("");

  const verify = async () => {
    const res = await verifyOtp(email, otp);
    if (res.success) onSuccess();
    else alert("Invalid OTP");
  };

  return (
    <div className="card">
      <h2>Verify OTP</h2>
      <input
        placeholder="Enter OTP"
        value={otp}
        onChange={e => setOtp(e.target.value)}
      />
      <button onClick={verify}>Verify</button>
    </div>
  );
}
