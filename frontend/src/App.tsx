import { useState } from "react";

import { generateDraft } from "./api/client";
import type { Mode } from "./api/types";
import { ChatHeader } from "./components/ChatHeader";
import { ChatThread } from "./components/ChatThread";
import { GuideCard } from "./components/GuideCard";
import { Hero } from "./components/Hero";
import { MessageInput } from "./components/MessageInput";
import { ModeChips } from "./components/ModeChips";
import { Sidebar } from "./components/Sidebar";
import { ToneCard } from "./components/ToneCard";
import type { QuickAction } from "./quickActions";
import type { ChatMessage, PersonaMessage } from "./types";

/**
 * Single-persona app (decision A2.6): the UI always targets Van Keith, so the
 * persona id is a constant rather than dynamic state. `GET /api/personas` stays
 * live server-side but is no longer called from the frontend.
 */
const PERSONA_ID = "van_keith";

function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function App() {
  const [mode, setMode] = useState<Mode>("raw");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeActionId, setActiveActionId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  async function handleSend(text: string, modeOverride?: Mode) {
    const effectiveMode = modeOverride ?? mode;
    if (modeOverride && modeOverride !== mode) {
      setMode(modeOverride);
    }
    const userMsg: ChatMessage = { id: makeId(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setPending(true);
    setError(null);

    try {
      const response = await generateDraft({
        persona_id: PERSONA_ID,
        question: text,
        mode: effectiveMode,
      });
      const personaMsg: ChatMessage = {
        id: makeId(),
        role: "persona",
        draft: response.draft,
        alternate: response.alternate,
        guide: response.guide,
        mode: effectiveMode,
      };
      setMessages((prev) => [...prev, personaMsg]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setPending(false);
    }
  }

  function handleQuickAction(action: QuickAction) {
    setActiveActionId(action.id);
    setDrawerOpen(false);
    void handleSend(action.message, action.mode);
  }

  function handleFreeSend(text: string) {
    setActiveActionId(null);
    void handleSend(text);
  }

  const isWelcome = messages.length === 0 && !pending && !error;
  const quickActionsDisabled = pending;

  // The Guide card always reflects the most recent persona turn. On a fresh send
  // `pending` flips the card to its skeleton; the previous guide stays mounted
  // underneath the state so a failed send degrades quietly to the last good one.
  const lastPersonaMessage = [...messages]
    .reverse()
    .find((msg): msg is PersonaMessage => msg.role === "persona");
  const guideTips = lastPersonaMessage?.guide ?? [];

  return (
    <div className="app">
      <div className="app__glow app__glow--top" aria-hidden="true" />
      <div className="app__glow app__glow--bottom" aria-hidden="true" />

      <Sidebar
        onQuickAction={handleQuickAction}
        activeActionId={activeActionId}
        quickActionsDisabled={quickActionsDisabled}
      />

      <section className="center">
        <ChatHeader
          drawerOpen={drawerOpen}
          onToggleDrawer={() => setDrawerOpen((open) => !open)}
          onQuickAction={handleQuickAction}
          activeActionId={activeActionId}
          quickActionsDisabled={quickActionsDisabled}
        />

        <div className="center__scroll">
          {isWelcome ? (
            <Hero onQuickAction={handleQuickAction} disabled={quickActionsDisabled} />
          ) : (
            <ChatThread messages={messages} pending={pending} error={error} />
          )}
        </div>

        <div className="center__composer">
          <ModeChips mode={mode} onModeChange={setMode} />
          <MessageInput
            onSend={handleFreeSend}
            disabled={pending}
          />
        </div>
      </section>

      <aside className="rail" aria-label="Context">
        <div className="rail__label">Context</div>
        <GuideCard tips={guideTips} pending={pending} />
        <ToneCard mode={mode} onModeChange={setMode} />
      </aside>
    </div>
  );
}

export default App;
