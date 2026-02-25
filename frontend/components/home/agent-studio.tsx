"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

import {
  analyzeVision,
  MediaType,
  streamAnalyzeVision,
  streamQuestionVision,
  uploadMedia,
  VisionAnalyzeResponse,
} from "@/lib/ai-client";

import { Section } from "@/components/ui/section";

const mediaOptions: MediaType[] = ["image", "video", "webcam"];

export function AgentStudioSection() {
  const [mediaType, setMediaType] = useState<MediaType>("image");
  const [prompt, setPrompt] = useState("Describe the scene and key objects.");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<VisionAnalyzeResponse | null>(null);
  const [streamedText, setStreamedText] = useState("");
  const [question, setQuestion] = useState("What are the most important objects visible?");
  const [questionStream, setQuestionStream] = useState("");

  const canUpload = useMemo(() => mediaType !== "webcam", [mediaType]);

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(event.target.files?.[0] ?? null);
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsRunning(true);
    setError(null);
    setStreamedText("");
    setQuestionStream("");
    setAnalysis(null);

    try {
      let sourceUri: string | undefined;
      if (canUpload && selectedFile) {
        const upload = await uploadMedia(selectedFile, mediaType);
        sourceUri = upload.storage_uri as string;
      }

      const base = await analyzeVision({ media_type: mediaType, prompt, source_uri: sourceUri });
      setAnalysis(base);

      await streamAnalyzeVision(
        { media_type: mediaType, prompt, source_uri: sourceUri },
        (token) => setStreamedText((prev) => `${prev}${prev ? " " : ""}${token}`),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected analysis error.");
    } finally {
      setIsRunning(false);
    }
  };

  const onQuestion = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsRunning(true);
    setError(null);
    setQuestionStream("");
    try {
      await streamQuestionVision("studio-question", question, (token) =>
        setQuestionStream((prev) => `${prev}${prev ? " " : ""}${token}`),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected question stream error.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <Section id="agent-studio">
      <div className="mb-8 text-center">
        <p className="text-xs uppercase tracking-[0.32em] text-white/55">Vision Agent Studio</p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Run Real-Time Vision Analysis</h2>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <form onSubmit={onSubmit} className="glass-card rounded-2xl p-6">
          <label className="mb-2 block text-xs uppercase tracking-[0.22em] text-white/55">Media Type</label>
          <div className="mb-4 flex flex-wrap gap-2">
            {mediaOptions.map((option) => (
              <button
                key={option}
                type="button"
                onClick={() => setMediaType(option)}
                className={`rounded-lg px-3 py-2 text-xs uppercase tracking-[0.14em] ${
                  mediaType === option ? "bg-cyan-300 text-slate-900" : "border border-white/20 text-white/75"
                }`}
              >
                {option}
              </button>
            ))}
          </div>

          {canUpload && (
            <>
              <label className="mb-2 block text-xs uppercase tracking-[0.22em] text-white/55">Upload File</label>
              <input
                type="file"
                accept={mediaType === "image" ? "image/*" : "video/*"}
                onChange={onFileChange}
                className="mb-4 w-full rounded-lg border border-white/20 bg-white/[0.02] p-2.5 text-sm text-white/80"
              />
            </>
          )}

          <label className="mb-2 block text-xs uppercase tracking-[0.22em] text-white/55">Prompt</label>
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            rows={4}
            className="mb-5 w-full rounded-lg border border-white/20 bg-white/[0.02] p-3 text-sm text-white/85"
          />

          <button
            type="submit"
            disabled={isRunning}
            className="neon-ring w-full rounded-xl bg-cyan-300/90 px-4 py-3 text-sm font-medium text-slate-950 disabled:opacity-70"
          >
            {isRunning ? "Running Analysis..." : "Analyze with Vision Agent"}
          </button>
        </form>

        <div className="space-y-4">
          <div className="glass-card rounded-2xl p-6">
            <p className="text-xs uppercase tracking-[0.22em] text-white/55">Analysis Summary</p>
            <p className="mt-3 text-sm text-white/82">{analysis?.summary ?? "Run analysis to see AI summary."}</p>
          </div>
          <div className="glass-card rounded-2xl p-6">
            <p className="text-xs uppercase tracking-[0.22em] text-white/55">Streaming Tokens</p>
            <p className="mt-3 min-h-20 text-sm text-cyan-100/85">{streamedText || "Waiting for stream..."}</p>
          </div>
          <form onSubmit={onQuestion} className="glass-card rounded-2xl p-6">
            <p className="text-xs uppercase tracking-[0.22em] text-white/55">Question Streaming</p>
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              className="mt-3 w-full rounded-lg border border-white/20 bg-white/[0.02] p-3 text-sm text-white/85"
            />
            <button
              type="submit"
              disabled={isRunning}
              className="mt-3 w-full rounded-lg border border-cyan-300/40 px-4 py-2.5 text-sm font-medium text-cyan-100"
            >
              Stream Answer
            </button>
            <p className="mt-3 min-h-16 text-sm text-cyan-100/85">{questionStream || "Waiting for answer stream..."}</p>
          </form>
          {error && <div className="rounded-xl border border-rose-300/40 bg-rose-500/10 p-3 text-sm text-rose-100">{error}</div>}
        </div>
      </div>
    </Section>
  );
}
