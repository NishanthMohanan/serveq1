import { useState } from "react";
import { sendOtp } from "../services/api";

export default function Login({ onNext }) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [generatedOtp, setGeneratedOtp] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!email || !username) {
      alert("Please enter username and email");
      return;
    }

    setLoading(true);
    try {
      const res = await sendOtp(email, username);
      setGeneratedOtp(res.otp);
    } catch (err) {
      alert("Failed to generate OTP");
    } finally {
      setLoading(false);
    }
  };

  return (
    
    <div className="card">
      <h2>Login</h2>

      <input
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        placeholder="Email address"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <button
        className="primary-btn"
        onClick={submit}
        disabled={loading}
      >
        {loading ? "Generating OTP..." : "Generate OTP"}
      </button>

      {generatedOtp && (
        <div className="alert">
          Demo OTP: <strong>{generatedOtp}</strong>
          <br />
          <button
            className="primary-btn"
            onClick={() => onNext(email)}
          >
            Continue
          </button>
        </div>
      )}
    </div>
  );
}
