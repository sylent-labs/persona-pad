import type { GenerateRequest, GenerateResponse } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function generateDraft(req: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch(`${BASE_URL}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`Generate failed (${response.status}): ${detail || response.statusText}`);
  }

  return (await response.json()) as GenerateResponse;
}
