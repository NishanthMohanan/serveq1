import { useEffect, useState } from "react";

export default function Queue({ slot }) {
  const [position, setPosition] = useState(5);

  useEffect(() => {
    const timer = setInterval(() => {
      setPosition(p => Math.max(1, p - 1));
    }, 4000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="card">
      <h2>Queue Status</h2>
      <p>Slot: {slot}</p>
      <p>Your Position: {position}</p>

      {position === 1 && (
        <div className="alert">🔔 Your appointment is in 10 minutes</div>
      )}
    </div>
  );
}
