import React from "react";
import { render, screen } from "@testing-library/react";

import { LiveVisionLabSection } from "@/components/home/live-vision-lab";

vi.mock("@/components/home/use-live-vision-agent", () => ({
  useLiveVisionAgent: () => ({
    connected: false,
    detections: [],
    reasoning: "",
    tokens: [],
    events: [],
    error: null,
    connect: vi.fn(),
    disconnect: vi.fn(),
    sendFrame: vi.fn(),
    askQuestion: vi.fn(),
    brainState: "INITIALIZING",
    stateConfidence: 0,
    stateReason: "",
    stateSince: Date.now(),
    transitions: [],
    alerts: [],
    summary: "",
    behaviorLabel: "",
  }),
}));

describe("LiveVisionLabSection", () => {
  it("renders live vision controls", () => {
    render(<LiveVisionLabSection />);
    expect(screen.getByText("Real-Time Cognitive Vision Agent")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Connect Live Agent" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ask Agent" })).toBeInTheDocument();
  });
});
