interface BrandMarkProps {
  /** Pixel size of the square mark. Defaults to the sidebar size. */
  size?: number;
}

/**
 * The VKI brand chip: a gradient rounded square with the "+" core motif, a
 * scaled-down echo of the hero orb. Hand-coded so it stays var/gradient driven.
 */
export function BrandMark({ size = 34 }: BrandMarkProps) {
  return (
    <span
      className="brand-mark"
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 5v14M5 12h14"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
        />
      </svg>
    </span>
  );
}
