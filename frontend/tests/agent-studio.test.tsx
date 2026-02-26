import React from "react";
import { render, screen } from "@testing-library/react";

import { AgentStudioSection } from "@/components/home/agent-studio";

vi.mock("@/lib/ai-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/ai-client")>("@/lib/ai-client");
  return {
    ...actual,
    getVisionCapabilities: vi.fn(async () => ({
      supported_media_types: ["image", "video", "webcam"],
      supported_transports: ["rest", "websocket"],
      supports_streaming: true,
      model: "gpt-4.1-mini",
      openai_enabled: false,
      fallback_mode: true,
    })),
  };
});

describe("AgentStudioSection", () => {
  it("renders studio heading and analyze action", async () => {
    render(<AgentStudioSection />);

    expect(screen.getByText("Run Real-Time Vision Analysis")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze with Vision Agent" })).toBeInTheDocument();
    expect(await screen.findByText(/Model:/)).toBeInTheDocument();
  });
});
