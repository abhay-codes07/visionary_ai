from __future__ import annotations

import logging

from app.core.config import Settings, get_settings
from app.schemas.live import LiveDetection

logger = logging.getLogger(__name__)


class VisionAgentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._agent = self._build_agent() if self._settings.visionagents_enabled else None

    async def reason(self, prompt: str, detections: list[LiveDetection], demo_mode: str = "custom") -> str:
        if self._agent is not None:
            try:
                return await self._agent_reason(prompt=prompt, detections=detections, demo_mode=demo_mode)
            except Exception:
                logger.debug("[agent] vision-agent reason failed, falling back to stub")
        result = self._fallback_reason(prompt=prompt, detections=detections, demo_mode=demo_mode)
        logger.debug("[agent] fallback reasoning: %s", result[:80])
        return result

    async def answer_question(self, question: str, detections: list[LiveDetection], demo_mode: str = "custom") -> str:
        if self._agent is not None:
            try:
                return await self._agent_reason(prompt=question, detections=detections, demo_mode=demo_mode)
            except Exception:
                pass
        labels = ", ".join(sorted({d.label for d in detections})) or "no clear objects"
        return f"Based on live video ({demo_mode}), answer to '{question}': detected {labels}."

    def _build_agent(self):
        try:
            from vision_agent import Agent

            return Agent(name="visionary-live-agent")
        except Exception:
            return None

    async def _agent_reason(self, prompt: str, detections: list[LiveDetection], demo_mode: str) -> str:
        label_text = ", ".join([f"{d.label}({d.confidence:.2f})" for d in detections]) or "none"
        message = (
            f"Demo mode: {demo_mode}. Prompt: {prompt}. "
            f"Detected objects: {label_text}. Provide concise real-time reasoning."
        )
        result = await self._agent.run(message)
        return str(result).strip()

    @staticmethod
    def _fallback_reason(prompt: str, detections: list[LiveDetection], demo_mode: str) -> str:
        labels = ", ".join(sorted({d.label for d in detections})) or "no strong detections"
        if demo_mode == "security":
            return f"[security] Monitoring update: detected {labels}. Prompt '{prompt}'. Escalate if unknown motion persists."
        if demo_mode == "workspace":
            return f"[workspace] Productivity context: observed {labels}. Prompt '{prompt}'. User appears engaged with workstation."
        if demo_mode == "objects":
            return f"[objects] Inventory stream: {labels}. Prompt '{prompt}'. Tracking object presence in frame."
        return f"[custom] Prompt '{prompt}' interpreted with live detections: {labels}."
