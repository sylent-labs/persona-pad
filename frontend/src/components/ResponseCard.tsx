import { useState } from "react";

interface ResponseCardProps {
  title: string;
  body: string;
}

export function ResponseCard({ title, body }: ResponseCardProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(body);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard API can fail in insecure contexts; surface as no-op rather than crash
      setCopied(false);
    }
  }

  return (
    <article className="card">
      <header className="card-header">
        <h2>{title}</h2>
        <button type="button" onClick={handleCopy} aria-label={`Copy ${title}`}>
          {copied ? "Copied!" : "Copy"}
        </button>
      </header>
      <p className="card-body">{body}</p>
    </article>
  );
}
