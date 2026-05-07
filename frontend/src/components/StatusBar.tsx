import { useEffect, useState } from "react";

function formatClock(date: Date): string {
  const hours = date.getHours();
  const minutes = date.getMinutes().toString().padStart(2, "0");
  const display = ((hours + 11) % 12) + 1;
  return `${display}:${minutes}`;
}

export function StatusBar() {
  const [now, setNow] = useState(() => formatClock(new Date()));

  useEffect(() => {
    const id = window.setInterval(() => setNow(formatClock(new Date())), 30_000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="status-bar" aria-hidden="true">
      <span className="status-bar__time">{now}</span>
      <span className="status-bar__icons">
        {/* signal */}
        <svg width="17" height="11" viewBox="0 0 17 11" fill="currentColor">
          <rect x="0" y="7" width="3" height="4" rx="0.5" />
          <rect x="4.5" y="5" width="3" height="6" rx="0.5" />
          <rect x="9" y="3" width="3" height="8" rx="0.5" />
          <rect x="13.5" y="0" width="3" height="11" rx="0.5" />
        </svg>
        {/* wifi */}
        <svg width="15" height="11" viewBox="0 0 15 11" fill="currentColor">
          <path d="M7.5 9.5a1 1 0 100 2 1 1 0 000-2zM2.6 5.6a7 7 0 019.8 0l1-1A8.4 8.4 0 001.6 4.6l1 1zM4.6 7.6a4.2 4.2 0 015.8 0l1-1a5.6 5.6 0 00-7.8 0l1 1z" />
        </svg>
        {/* battery */}
        <svg width="26" height="11" viewBox="0 0 26 11" fill="none">
          <rect
            x="0.5"
            y="0.5"
            width="22"
            height="10"
            rx="2.5"
            stroke="currentColor"
            strokeOpacity="0.5"
          />
          <rect x="2" y="2" width="19" height="7" rx="1.2" fill="currentColor" />
          <rect x="23.5" y="3.5" width="1.5" height="4" rx="0.5" fill="currentColor" fillOpacity="0.5" />
        </svg>
      </span>
    </div>
  );
}
