export type MediaType = "image" | "video" | "webcam";

export type VisionAnalyzeRequest = {
  media_type: MediaType;
  prompt: string;
  source_uri?: string;
};

export type VisionAnalyzeResponse = {
  request_id: string;
  media_type: MediaType;
  summary: string;
  detections: Array<{ label: string; confidence: number; description: string }>;
  generated_at: string;
};

export type VisionCapabilities = {
  supported_media_types: MediaType[];
  supported_transports: string[];
  supports_streaming: boolean;
  model: string;
  openai_enabled: boolean;
  fallback_mode: boolean;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

export async function analyzeVision(payload: VisionAnalyzeRequest): Promise<VisionAnalyzeResponse> {
  const response = await fetch(`${API_V1}/vision/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Analyze request failed: ${response.status}`);
  }
  return response.json() as Promise<VisionAnalyzeResponse>;
}

export async function getVisionCapabilities(): Promise<VisionCapabilities> {
  const response = await fetch(`${API_V1}/vision/capabilities`);
  if (!response.ok) {
    throw new Error(`Capabilities request failed: ${response.status}`);
  }
  return response.json() as Promise<VisionCapabilities>;
}

export async function uploadMedia(file: File, mediaType: MediaType) {
  const form = new FormData();
  form.append("media_type", mediaType);
  form.append("file", file);
  const response = await fetch(`${API_V1}/vision/upload`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(`Upload request failed: ${response.status}`);
  }
  return response.json();
}

export async function streamAnalyzeVision(payload: VisionAnalyzeRequest, onToken: (token: string) => void) {
  const response = await fetch(`${API_V1}/vision/analyze/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Stream request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const line = event.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        const chunk = JSON.parse(data) as { token?: string };
        if (chunk.token) onToken(chunk.token);
      } catch {
        // Ignore malformed chunks.
      }
    }
  }
}

export async function streamQuestionVision(
  requestId: string,
  question: string,
  onToken: (token: string) => void,
) {
  const response = await fetch(`${API_V1}/vision/question/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: requestId, question }),
  });
  if (!response.ok || !response.body) {
    throw new Error(`Question stream request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const line = event.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        const chunk = JSON.parse(data) as { token?: string };
        if (chunk.token) onToken(chunk.token);
      } catch {
        // Ignore malformed chunks.
      }
    }
  }
}

export function createVisionWebSocket(): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/v1/ws";
  return new WebSocket(wsUrl);
}
