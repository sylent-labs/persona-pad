interface GuideCardProps {
  /** The guide bullets from the most recent persona turn. Empty before any send. */
  tips: string[];
  /** A draft is in flight; the guide is part of that same call, so show a skeleton. */
  pending: boolean;
}

const SKELETON_ROWS = 4;

/**
 * Right-rail Guide card. The guide arrives in the same `/api/generate` call as the
 * draft (one LLM call, dissected client-side), so this card has no fetch of its own —
 * it renders whatever the latest persona turn carried. Three states: welcome (no
 * send yet), loading (a draft is in flight), and populated (4 strategy bullets).
 */
export function GuideCard({ tips, pending }: GuideCardProps) {
  const hasTips = tips.length > 0;

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

      {pending ? (
        <GuideSkeleton />
      ) : hasTips ? (
        <>
          <ul className="guide-card__tips">
            {tips.map((tip) => (
              <li key={tip} className="guide-card__tip">
                {tip}
              </li>
            ))}
          </ul>
          <div className="guide-card__status">
            <span className="guide-card__dot" aria-hidden="true" />
            Updated for your last message
          </div>
        </>
      ) : (
        <p className="guide-card__body">
          Send a message and I&apos;ll lay out how Van Keith would reply — and how
          to play it.
        </p>
      )}
    </div>
  );
}

function GuideSkeleton() {
  return (
    <div className="guide-card__skeleton" aria-hidden="true">
      {Array.from({ length: SKELETON_ROWS }, (_, i) => (
        <span key={i} className="guide-card__skeleton-row" />
      ))}
    </div>
  );
}
