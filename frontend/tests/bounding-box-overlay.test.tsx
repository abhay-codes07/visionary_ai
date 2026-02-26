import { render } from "@testing-library/react";

import { BoundingBoxOverlay } from "@/components/BoundingBoxOverlay";

describe("BoundingBoxOverlay", () => {
  it("renders boxes for detections", () => {
    const detections = [
      { label: "person", confidence: 0.98, box: { x: 20, y: 30, width: 100, height: 180 } },
    ];

    const { container } = render(
      <BoundingBoxOverlay detections={detections} sourceWidth={640} sourceHeight={360} />,
    );

    expect(container.querySelectorAll(".absolute").length).toBeGreaterThan(0);
  });
});
