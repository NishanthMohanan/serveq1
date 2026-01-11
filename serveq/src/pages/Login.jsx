import { useState } from "react";
import { sendOtp } from "../services/api";

export default function Login({ onNext }) {
  const [email, setEmail] = useState("");
  const [generatedOtp, setGeneratedOtp] = useState(null);

  const submit = async () => {
    const res = await sendOtp(email);
    setGeneratedOtp(res.otp);
  };

  return (
    <div className="card">
      <h2>Login</h2>

      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <button onClick={submit}>Generate OTP</button>

      {generatedOtp && (
        <div className="alert">
          Demo OTP: <strong>{generatedOtp}</strong>
          <br />
          <button onClick={() => onNext(email)}>
            Continue to Verify
          </button>
        </div>
      )}
    </div>
  );
}
