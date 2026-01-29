import { useEffect, useState } from "react";
import { fetchSlots, bookSlot } from "../services/api";

function getNext7Days() {
  return [...Array(7)].map((_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    return d.toISOString().split("T")[0];
  });
}

export default function Slots({ email, onBooked }) {
  const dates = getNext7Days();
  const [selectedDate, setSelectedDate] = useState(dates[0]);
  const [slots, setSlots] = useState([]);

  useEffect(() => {
    fetchSlots(selectedDate).then(res => setSlots(res.slots));
  }, [selectedDate]);

  const book = async (slot) => {
    if (!slot.is_bookable) return;
    await bookSlot(email, `${selectedDate} ${slot.start}-${slot.end}`);
    onBooked(`${selectedDate} ${slot.start} - ${slot.end}`);
  };

  return (
    <div className="card">
      <h2>Select Date</h2>

      <select
        value={selectedDate}
        onChange={(e) => setSelectedDate(e.target.value)}
      >
        {dates.map(d => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>

      <h3>Available Slots</h3>

      {slots.map((s, i) => (
        <button
          key={i}
          className="slot-btn"
          disabled={!s.is_bookable}
          onClick={() => book(s)}
          style={{ opacity: s.is_bookable ? 1 : 0.5 }}
        >
          {s.start} – {s.end}
        </button>
      ))}
    </div>
  );
}
