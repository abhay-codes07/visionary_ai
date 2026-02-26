import React from "react";
import { render, screen } from "@testing-library/react";

import { LiveAgentFeedSection } from "@/components/home/live-agent-feed";

vi.mock("@/lib/ai-client", async () => {
  const actual = await vi.importActual<typeof import("@/lib/ai-client")>("@/lib/ai-client");
  return {
    ...actual,
    createVisionWebSocket: vi.fn(() => new WebSocket("ws://localhost/mock")),
  };
});

describe("LiveAgentFeedSection", () => {
  it("renders websocket controls", () => {
    render(<LiveAgentFeedSection />);

    expect(screen.getByText("WebSocket Live Agent Feed")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Connect" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Send Analyze" })).toBeInTheDocument();
  });
});
