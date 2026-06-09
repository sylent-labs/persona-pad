/**
 * Right-rail Guide card. PR2 ships only the placeholder/empty state — the
 * `/api/guide` call and populated bullets land in PR3. The slot is here so the
 * rail layout is final.
 */
export function GuideCard() {
  return (
    <div className="guide-card">
      <div className="guide-card__head">
        <span className="guide-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M12 3l1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8L12 3z" />
          </svg>
        </span>
        <div>
          <div className="card__title">Guide</div>
          <div className="card__subtitle">Updates with each message</div>
        </div>
      </div>
      <p className="guide-card__body">
        Send a message and I&apos;ll lay out how Van Keith would reply — and how
        to play it.
      </p>
    </div>
  );
}
