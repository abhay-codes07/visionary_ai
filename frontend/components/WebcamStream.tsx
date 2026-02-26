"use client";

import { useEffect, useRef } from "react";

type WebcamStreamProps = {
  active: boolean;
  fps?: number;
  onFrame: (base64Image: string) => void;
};

export function WebcamStream({ active, fps = 6, onFrame }: WebcamStreamProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (!active) return;
    let intervalId: number | undefined;
    let mounted = true;

    const boot = async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 960 }, height: { ideal: 540 } },
        audio: false,
      });
      if (!mounted) return;
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      intervalId = window.setInterval(() => {
        if (!videoRef.current || !canvasRef.current) return;
        const w = videoRef.current.videoWidth;
        const h = videoRef.current.videoHeight;
        if (!w || !h) return;
        canvasRef.current.width = w;
        canvasRef.current.height = h;
        const ctx = canvasRef.current.getContext("2d");
        if (!ctx) return;
        ctx.drawImage(videoRef.current, 0, 0, w, h);
        const dataUrl = canvasRef.current.toDataURL("image/jpeg", 0.75);
        const base64 = dataUrl.split(",")[1] ?? "";
        if (base64) onFrame(base64);
      }, Math.max(80, Math.floor(1000 / fps)));
    };

    void boot();
    return () => {
      mounted = false;
      if (intervalId) clearInterval(intervalId);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, [active, fps, onFrame]);

  return (
    <div className="relative w-full overflow-hidden rounded-xl border border-white/15 bg-black/20">
      <video ref={videoRef} playsInline muted className="h-auto w-full" />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
