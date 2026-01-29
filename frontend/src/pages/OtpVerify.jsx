import { useState } from "react";
import { verifyOtp } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function OtpVerify({ email, onSuccess }) {
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const verify = async () => {
    if (!otp) {
      setError("Enter OTP");
      return;
    }
    
    setLoading(true);
    setError("");
    try {
      const res = await verifyOtp(email, otp);
      if (res.success) {
        onSuccess();
      } else {
        setError(res.error || "Invalid OTP");
      }
    } catch (err) {
      setError(err.message || "Failed to verify OTP");
    } finally {
      setLoading(false);
    }
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

      {error && <div className="alert error">{error}</div>}

      <input
        placeholder="Enter OTP"
        value={otp}
        onChange={(e) => setOtp(e.target.value)}
      />
      <button className="primary-btn" onClick={verify} disabled={loading}>
        {loading ? "Verifying..." : "Verify"}
      </button>
    </div>
  );
}
