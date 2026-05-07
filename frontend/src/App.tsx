import { useState } from "react";

import { generateDraft } from "./api/client";
import type { GenerateRequest, GenerateResponse } from "./api/types";
import { ChatBox } from "./components/ChatBox";
import { ResponseCard } from "./components/ResponseCard";

function App() {
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(req: GenerateRequest) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await generateDraft(req);
      setResult(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="app-header">
        <h1>Persona Pad</h1>
        <p className="tagline">
          Drafts replies in VK&apos;s voice. Donna reviews and copies. We do not
          pretend to <em>be</em> VK.
        </p>
      </header>

      <ChatBox onSubmit={handleSubmit} loading={loading} />

      {error ? <div className="error">{error}</div> : null}

      {result ? (
        <section className="results">
          <ResponseCard title="Draft" body={result.draft} />
          <ResponseCard title="Alternate" body={result.alternate} />
          {result.style_notes.length > 0 ? (
            <aside className="style-notes">
              <h3>Style notes</h3>
              <ul>
                {result.style_notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
            </aside>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}

export default App;
