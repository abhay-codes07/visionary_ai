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

export type SystemStatus = {
  status: string;
  started_at: string;
  uptime_seconds: number;
  openai_enabled: boolean;
  fallback_mode: boolean;
};

export type LiveBoundingBox = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type LiveDetection = {
  label: string;
  confidence: number;
  box: LiveBoundingBox;
};

export type LiveStreamEvent = {
  type: "detection" | "reasoning" | "token" | "session" | "error";
  session_id: string;
  frame_id?: string;
  content: string;
  detections?: LiveDetection[];
  timestamp: string;
};

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, "");
const API_V1 = API_BASE.endsWith("/api/v1") ? API_BASE : `${API_BASE}/api/v1`;

async function toApiError(response: Response, fallback: string): Promise<Error> {
  try {
    const payload = (await response.json()) as { error?: { message?: string } };
    if (payload?.error?.message) return new Error(payload.error.message);
  } catch {
    // ignore parse errors
  }
  return new Error(`${fallback}: ${response.status}`);
}

export async function analyzeVision(payload: VisionAnalyzeRequest): Promise<VisionAnalyzeResponse> {
  const response = await fetch(`${API_V1}/vision/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw await toApiError(response, "Analyze request failed");
  }
  return response.json() as Promise<VisionAnalyzeResponse>;
}

export async function getVisionCapabilities(): Promise<VisionCapabilities> {
  const response = await fetch(`${API_V1}/vision/capabilities`);
  if (!response.ok) {
    throw await toApiError(response, "Capabilities request failed");
  }
  return response.json() as Promise<VisionCapabilities>;
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_V1}/system/status`);
  if (!response.ok) {
    throw await toApiError(response, "System status request failed");
  }
  return response.json() as Promise<SystemStatus>;
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
    throw await toApiError(response, "Upload request failed");
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
    throw await toApiError(response, "Stream request failed");
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
    throw await toApiError(response, "Question stream request failed");
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
  const wsUrl = (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/v1/ws").replace(/\/+$/, "");
  return new WebSocket(wsUrl);
}

export function createLiveVisionWebSocket(): WebSocket {
  const base = (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/api/v1/ws").replace(/\/+$/, "");
  const liveUrl = base.endsWith("/ws/live") ? base : base.replace(/\/ws$/, "/ws/live");
  return new WebSocket(liveUrl);
}
