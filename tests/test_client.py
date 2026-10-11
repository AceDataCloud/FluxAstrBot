"""Flux image request and terminal-result boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import FluxClient, FluxError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-flux"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_image_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"task_id": "task-123"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await FluxClient("test-key").submit("A ceramic vase")
    assert calls == [
        (
            "https://api.acedata.cloud/flux/images",
            {
                "action": "generate",
                "prompt": "A ceramic vase",
                "model": "flux-dev",
                "size": "1024x1024",
                "async": True,
                "count": 1,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert "image_urls" not in result


@pytest.mark.asyncio
async def test_edit_uses_kontext_and_authorized_https_reference():
    with patch(
        "client.OPENER.open", return_value=FakeResponse({"task_id": "task-456"})
    ) as opening:
        await FluxClient("test-key").submit(
            "Make it blue",
            model="flux-kontext-pro",
            image_url="https://example.org/vase.jpg",
        )
    payload = json.loads(opening.call_args.args[0].data)
    assert payload == {
        "action": "edit",
        "prompt": "Make it blue",
        "model": "flux-kontext-pro",
        "size": "1:1",
        "async": True,
        "image_url": "https://example.org/vase.jpg",
    }


@pytest.mark.asyncio
async def test_task_lookup_withholds_preview_and_keeps_public_cost():
    submitted = {"id": "task-123", "trace_id": "trace-flux"}
    preview = {
        "finished_at": None,
        "response": {
            "success": True,
            "data": [{"image_url": "https://cdn.example.org/preview.png"}],
        },
    }
    finished = {
        "finished_at": 123.0,
        "response": {
            "success": True,
            "data": [{"image_url": "https://cdn.example.org/final.png"}],
            "cost": {
                "amount": 0.216,
                "list_amount": 0.24,
                "currency": "credit",
                "supplier": "internal-only",
            },
        },
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(submitted),
            FakeResponse(preview),
            FakeResponse(finished),
        ],
    ) as opening:
        first = await FluxClient("test-key").query("task-123")
        second = await FluxClient("test-key").query("task-123")
        last = await FluxClient("test-key").query("task-123")
    assert opening.call_count == 3
    assert first["status"] == second["status"] == "pending"
    assert first["image_urls"] == second["image_urls"] == []
    assert last["status"] == "succeeded"
    assert last["image_urls"] == ["https://cdn.example.org/final.png"]
    assert last["cost"] == {
        "amount": 0.216,
        "list_amount": 0.24,
        "currency": "credit",
    }
    assert "supplier" not in str(last)


@pytest.mark.asyncio
async def test_invalid_input_never_submits_a_paid_job():
    client = FluxClient("test-key")
    for kwargs in (
        {"prompt": " "},
        {"prompt": "A vase", "model": "unknown"},
        {"prompt": "A vase", "model": "flux-2-pro", "size": "1024x1024"},
        {"prompt": "A vase", "model": "flux-2-klein", "size": "1792x1024"},
        {"prompt": "Edit", "image_url": "http://example.org/vase.jpg"},
        {
            "prompt": "Edit",
            "model": "flux-dev",
            "image_url": "https://example.org/vase.jpg",
        },
    ):
        with patch("client.OPENER.open") as opening, pytest.raises(FluxError):
            await client.submit(**kwargs)
        assert opening.call_count == 0
