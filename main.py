"""Flux image tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import FluxClient, FluxError


class FluxPlugin(Star):
    """Expose one image submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="flux_generate_image")
    async def flux_generate_image(
        self,
        event: AstrMessageEvent,
        prompt: str,
        model: str = "flux-dev",
        size: str = "",
        image_url: str = "",
    ) -> str:
        """Submit one billable Flux image generation or edit job.

        Args:
            prompt(string): Description of the image or requested edit.
            model(string): Flux model; use a Kontext model when editing.
            size(string): Optional model-compatible pixel size or aspect ratio.
            image_url(string): Optional authorized HTTPS image to edit.

        Returns:
            JSON submission status and task ID, never a finished-image claim.
        """
        try:
            result = await FluxClient(self.config.get("api_key", "")).submit(
                prompt, model, size, image_url
            )
        except FluxError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="flux_get_task")
    async def flux_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query a prior Flux task ID without another generation.

        Args:
            task_id(string): Exact task ID from flux_generate_image.

        Returns:
            JSON status and final image URLs only after task completion.
        """
        try:
            result = await FluxClient(self.config.get("api_key", "")).query(task_id)
        except FluxError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
