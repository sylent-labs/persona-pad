import { useEffect, useState } from "react";

import { generateDraft, listPersonas } from "./api/client";
import type { Mode, Persona } from "./api/types";
import { ChatHeader } from "./components/ChatHeader";
import { ChatThread } from "./components/ChatThread";
import { MessageInput } from "./components/MessageInput";
import { PhoneFrame } from "./components/PhoneFrame";
import type { ChatMessage } from "./types";

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function App() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [personaId, setPersonaId] = useState<string>("");
  const [mode, setMode] = useState<Mode>("raw");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listPersonas()
      .then((items) => {
        if (cancelled) return;
        setPersonas(items);
        const first = items[0];
        if (first) {
          setPersonaId((prev) => prev || first.id);
        }
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Failed to load personas");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSend(text: string) {
    if (!personaId) {
      setError("No persona selected");
      return;
    }
    const userMsg: ChatMessage = { id: makeId(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setPending(true);
    setError(null);

    try {
      const response = await generateDraft({
        persona_id: personaId,
        question: text,
        mode,
      });
      const draftMsg: ChatMessage = {
        id: makeId(),
        role: "persona",
        text: response.draft,
      };
      const alternateMsg: ChatMessage | null = response.alternate
        ? { id: makeId(), role: "persona", text: response.alternate }
        : null;

      setMessages((prev) =>
        alternateMsg ? [...prev, draftMsg, alternateMsg] : [...prev, draftMsg],
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setPending(false);
    }
  }

  function handlePersonaChange(nextId: string) {
    setPersonaId(nextId);
    setMessages([]);
    setError(null);
  }

  const emptyHint =
    personas.length === 0
      ? "Loading personas..."
      : "Send a message to start the conversation.";

  return (
    <main className="app">
      <PhoneFrame>
        <ChatHeader
          personas={personas}
          personaId={personaId}
          onPersonaChange={handlePersonaChange}
        />
        <ChatThread
          messages={messages}
          pending={pending}
          error={error}
          emptyHint={emptyHint}
        />
        <MessageInput
          onSend={handleSend}
          mode={mode}
          onModeChange={setMode}
          disabled={pending || !personaId}
        />
      </PhoneFrame>
    </main>
  );
}

export default App;
