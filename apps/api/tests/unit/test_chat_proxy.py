"""Tests for chat_proxy service."""
import httpx
import pytest

from ailiance_demo.services.chat_proxy import (
    ChatRequest,
    is_chat_eligible,
    stream_chat,
    AILIANCE_ALIASES,
)


def test_is_chat_eligible_returns_true_for_ailiance_aliases() -> None:
    for alias in AILIANCE_ALIASES:
        assert is_chat_eligible(alias) is True


def test_is_chat_eligible_returns_false_for_hf_models() -> None:
    assert is_chat_eligible("Ailiance-fr/micro-kiki-v3") is False
    assert is_chat_eligible("Ailiance-fr/mascarade-iot") is False


@pytest.mark.asyncio
async def test_stream_chat_forwards_sse_events() -> None:
    async def server_handler(request: httpx.Request) -> httpx.Response:
        async def emit():
            yield b'event: token\ndata: {"text":"Hello"}\n\n'
            yield b'event: token\ndata: {"text":" world"}\n\n'
            yield b'event: done\ndata: {}\n\n'
        return httpx.Response(200, content=emit(), headers={"content-type": "text/event-stream"})

    transport = httpx.MockTransport(server_handler)

    chat_req = ChatRequest(
        model_id="ailiance/mistral-medium-3.5-128b",
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.7,
    )

    chunks: list[bytes] = []
    async for chunk in stream_chat(
        chat_req,
        gateway_url="http://gateway:9200",
        http_transport=transport,
    ):
        chunks.append(chunk)

    raw = b"".join(chunks)
    assert b'event: token' in raw
    assert b'"text":"Hello"' in raw
    assert b'event: done' in raw


@pytest.mark.asyncio
async def test_stream_chat_consumes_reasoning_field() -> None:
    """DeepSeek-R1 distill emits delta.reasoning (OpenAI Reasoning API).

    The proxy must yield those tokens, otherwise reasoning-r1 streams empty.
    """

    async def server_handler(request: httpx.Request) -> httpx.Response:
        async def emit():
            # Upstream gateway forwards mlx_lm.server reasoning deltas
            # verbatim. No `content` field, only `reasoning`.
            yield (
                b'data: {"choices":[{"delta":'
                b'{"reasoning":"Let me think"}}]}\n\n'
            )
            yield (
                b'data: {"choices":[{"delta":'
                b'{"reasoning":" about it."}}]}\n\n'
            )
            yield b'data: [DONE]\n\n'

        return httpx.Response(
            200,
            content=emit(),
            headers={"content-type": "text/event-stream"},
        )

    transport = httpx.MockTransport(server_handler)

    chat_req = ChatRequest(
        model_id="ailiance/reasoning-r1",
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.7,
    )

    chunks: list[bytes] = []
    async for chunk in stream_chat(
        chat_req,
        gateway_url="http://gateway:9200",
        http_transport=transport,
    ):
        chunks.append(chunk)

    raw = b"".join(chunks)
    assert b'"text": "Let me think"' in raw
    assert b'"text": " about it."' in raw
    assert b'event: done' in raw


@pytest.mark.asyncio
async def test_stream_chat_still_consumes_content_field() -> None:
    """Non-regression: classical chat models keep emitting delta.content."""

    async def server_handler(request: httpx.Request) -> httpx.Response:
        async def emit():
            yield (
                b'data: {"choices":[{"delta":'
                b'{"content":"Hello"}}]}\n\n'
            )
            yield b'data: [DONE]\n\n'

        return httpx.Response(
            200,
            content=emit(),
            headers={"content-type": "text/event-stream"},
        )

    transport = httpx.MockTransport(server_handler)

    chat_req = ChatRequest(
        model_id="ailiance/mistral-medium-3.5-128b",
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.7,
    )

    chunks: list[bytes] = []
    async for chunk in stream_chat(
        chat_req,
        gateway_url="http://gateway:9200",
        http_transport=transport,
    ):
        chunks.append(chunk)

    raw = b"".join(chunks)
    assert b'"text": "Hello"' in raw
    assert b'event: done' in raw
