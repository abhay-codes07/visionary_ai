"use client";

import React from "react";

import { LiveDetection } from "@/lib/ai-client";

type BoundingBoxOverlayProps = {
  detections: LiveDetection[];
  sourceWidth: number;
  sourceHeight: number;
};

export function BoundingBoxOverlay({ detections, sourceWidth, sourceHeight }: BoundingBoxOverlayProps) {
  if (!sourceWidth || !sourceHeight) return null;

  return (
    <div className="pointer-events-none absolute inset-0">
      {detections.map((detection, index) => {
        const { x, y, width, height } = detection.box;
        const left = `${(x / sourceWidth) * 100}%`;
        const top = `${(y / sourceHeight) * 100}%`;
        const w = `${(width / sourceWidth) * 100}%`;
        const h = `${(height / sourceHeight) * 100}%`;
        return (
          <div
            key={`${detection.label}-${index}`}
            className="absolute border-2 border-cyan-300/90 bg-cyan-400/10"
            style={{ left, top, width: w, height: h }}
          >
            <div className="absolute -top-6 left-0 rounded-md bg-black/70 px-2 py-0.5 text-xs text-cyan-100">
              {detection.label} {(detection.confidence * 100).toFixed(0)}%
            </div>
          </div>
        );
      })}
    </div>
  );
}
