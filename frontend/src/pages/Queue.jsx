import { useEffect, useState } from "react";

export default function Queue({ slot }) {
  const [position, setPosition] = useState(5);

  useEffect(() => {
    const timer = setInterval(() => {
      setPosition(p => (p > 1 ? p - 1 : 1));
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="card">
      <h2>Queue Status</h2>
      <div className="queue-box">
        <p><strong>Slot:</strong> {slot}</p>
        <p><strong>Position:</strong> {position}</p>
      </div>

      {position === 1 && (
        <div className="banner success">
          🔔 Your appointment is in 10 minutes
        </div>
      )}
    </div>
  );
}
