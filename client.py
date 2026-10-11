"""Single-image Flux submission and existing-task lookup for AstrBot."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.acedata.cloud"
GENERATE_MODELS = {
    "flux-dev",
    "flux-pro",
    "flux-2-klein",
    "flux-2-flex",
    "flux-2-pro",
    "flux-2-max",
}
EDIT_MODELS = {"flux-kontext-pro", "flux-kontext-max"}
RATIO_MODELS = {"flux-2-flex", "flux-2-pro", "flux-2-max"} | EDIT_MODELS
RATIOS = {"21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21"}
PIXEL_SIZES = {"1024x1024", "1024x1792", "1792x1024"}


class _NoRedirect(HTTPRedirectHandler):
    """Never forward the configured key to a different host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


OPENER = build_opener(_NoRedirect)


class FluxError(RuntimeError):
    """An error safe to return to an AstrBot conversation."""


def _valid_https_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and not parsed.username
        and not parsed.password
    )


class FluxClient:
    """Submit one image job or read an already submitted Flux task."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise FluxError(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.0",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                header_trace = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise FluxError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check service access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise FluxError(
                "The API connection failed. Check request history before submitting again."
            ) from None
        except (ValueError, UnicodeError):
            raise FluxError(
                "The API returned invalid JSON. Check request history before retrying."
            ) from None
        if not isinstance(body, dict):
            raise FluxError("The API returned an unexpected response format.")
        return body, str(body.get("trace_id") or header_trace)

    async def submit(
        self,
        prompt: str,
        model: str = "flux-dev",
        size: str = "",
        image_url: str = "",
    ) -> dict[str, Any]:
        """Submit exactly one asynchronous image job, without paid retries."""
        prompt = prompt.strip()
        if not prompt or len(prompt) > 4000:
            raise FluxError("Provide an image prompt of 1–4000 characters.")
        if image_url:
            if not _valid_https_url(image_url):
                raise FluxError("Provide an authorized HTTPS reference image URL.")
            if model not in EDIT_MODELS:
                raise FluxError(
                    "Image editing requires flux-kontext-pro or flux-kontext-max."
                )
            action = "edit"
        else:
            if model not in GENERATE_MODELS:
                raise FluxError(
                    "Choose a supported Flux generation model; Kontext models require an image URL."
                )
            action = "generate"
        if not size:
            size = "1:1" if model in RATIO_MODELS else "1024x1024"
        if model in RATIO_MODELS:
            if size not in RATIOS:
                raise FluxError("This model requires an aspect ratio such as 1:1.")
        elif model == "flux-2-klein" and size != "1024x1024":
            raise FluxError("flux-2-klein currently uses 1024x1024 in this plugin.")
        elif model != "flux-2-klein" and size not in PIXEL_SIZES:
            raise FluxError("This model requires 1024x1024, 1024x1792, or 1792x1024.")
        payload: dict[str, Any] = {
            "action": action,
            "prompt": prompt,
            "model": model,
            "size": size,
            "async": True,
        }
        if image_url:
            payload["image_url"] = image_url
        else:
            payload["count"] = 1
        body, trace_id = await asyncio.to_thread(self._post, "/flux/images", payload)
        if body.get("success") is False or body.get("error"):
            raise FluxError(
                "Image submission was rejected. Check request history before trying again."
            )
        task_id = body.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise FluxError(
                "No task ID was returned. Check request history before submitting again."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": trace_id,
            "next_step": "Query this same task ID; do not submit another image while it is pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Return final image URLs only after terminal task success."""
        task_id = task_id.strip()
        if not task_id or len(task_id) > 128:
            raise FluxError("Pass the exact task ID from Flux submission.")
        body, trace_id = await asyncio.to_thread(
            self._post, "/flux/tasks", {"id": task_id, "action": "retrieve"}
        )
        if body.get("success") is False or body.get("error"):
            raise FluxError("Task lookup failed. Check request history.")
        response = body.get("response")
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = None
        if not isinstance(response, dict):
            response = {}
        trace_id = str(response.get("trace_id") or body.get("trace_id") or trace_id)
        state = str(body.get("state") or body.get("status") or "").lower()
        if state in {"failed", "error", "cancelled", "canceled"} or (
            response.get("success") is False
        ):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "image_urls": [],
            }
        if not body.get("finished_at") or response.get("success") is not True:
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "pending",
                "success": False,
                "image_urls": [],
            }
        data = response.get("data")
        urls = (
            [
                item["image_url"]
                for item in data
                if isinstance(item, dict)
                and isinstance(item.get("image_url"), str)
                and _valid_https_url(item["image_url"])
            ]
            if isinstance(data, list)
            else []
        )
        cost = response.get("cost")
        public_cost = (
            {
                key: cost[key]
                for key in ("amount", "list_amount", "currency")
                if key in cost
            }
            if isinstance(cost, dict)
            else {}
        )
        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "status": "succeeded" if urls else "failed",
            "success": bool(urls),
            "image_urls": urls,
            "image_count": len(urls),
            "cost": public_cost,
        }
