import { useState } from "react";
import { verifyOtp } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function OtpVerify({ email, onSuccess }) {
  const [otp, setOtp] = useState("");
  const navigate = useNavigate();

  const verify = async () => {
    if (!otp) {
      alert("Enter OTP");
      return;
    }
    const res = await verifyOtp(email, otp);
    res.success ? onSuccess() : alert("Invalid OTP");
  };

  const handleClick = () => {
    if (window.history.length > 1) {
      navigate(-1);
    }
  }

  return (
    <div className="card">
      <button onClick={handleClick}>Exit</button>
      <h2>Verify OTP</h2>
      <input
        placeholder="Enter OTP"
        value={otp}
        onChange={(e) => setOtp(e.target.value)}
      />
      <button className="primary-btn" onClick={verify}>
        Verify
      </button>
    </div>
  );
}
