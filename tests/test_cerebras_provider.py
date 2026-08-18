"""Cerebras provider — factory wiring + init contract.

Full network calls aren't exercised here (would require the real SDK + a key).
These tests pin the contract that makes the config-swap fallback trustworthy:
  - factory dispatches to CerebrasProvider when LLM_PROVIDER=cerebras
  - missing key fails loud at construction, not later inside generate()
  - schema hint helper actually embeds the schema (this is what stands in for
    Groq's strict-mode constrained decoder on Cerebras' json_object path)
"""
from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _clear_provider_cache():
    from src import llm_client

    llm_client._get_provider.cache_clear()
    yield
    llm_client._get_provider.cache_clear()


def _install_fake_cerebras_sdk():
    """Insert a stub `cerebras.cloud.sdk` module so tests run without the real
    package installed. Returns the MagicMock Cerebras class for assertions."""
    fake_client_cls = MagicMock(name="Cerebras")
    mod_sdk = types.ModuleType("cerebras.cloud.sdk")
    mod_sdk.Cerebras = fake_client_cls
    mod_cloud = types.ModuleType("cerebras.cloud")
    mod_cloud.sdk = mod_sdk
    mod_root = types.ModuleType("cerebras")
    mod_root.cloud = mod_cloud
    sys.modules["cerebras"] = mod_root
    sys.modules["cerebras.cloud"] = mod_cloud
    sys.modules["cerebras.cloud.sdk"] = mod_sdk
    return fake_client_cls


def test_factory_dispatches_to_cerebras(monkeypatch):
    _install_fake_cerebras_sdk()
    monkeypatch.setattr("src.config.LLM_PROVIDER", "cerebras")
    monkeypatch.setattr("src.config.CEREBRAS_API_KEY", "test-key")

    from src import llm_client
    from src.llm_providers.cerebras import CerebrasProvider

    prov = llm_client._get_provider()
    assert isinstance(prov, CerebrasProvider)
    assert prov.name == "cerebras"


def test_missing_key_raises_at_construction(monkeypatch):
    _install_fake_cerebras_sdk()
    from src.llm_providers.cerebras import CerebrasProvider

    with pytest.raises(ValueError, match="CEREBRAS_API_KEY missing"):
        CerebrasProvider(api_key="")


def test_schema_hint_embeds_the_schema():
    from src.llm_providers.cerebras import _schema_hint

    schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
    hint = _schema_hint(schema)
    assert "SCHEMA:" in hint
    assert '"ok"' in hint
    assert '"boolean"' in hint
    assert "code fences" in hint or "No prose" in hint


def test_generate_returns_parsed_result(monkeypatch):
    fake_cls = _install_fake_cerebras_sdk()
    fake_client = MagicMock()
    fake_cls.return_value = fake_client

    usage = MagicMock(prompt_tokens=100, completion_tokens=50)
    choice = MagicMock()
    choice.message.content = '{"ok": true}'
    fake_client.chat.completions.create.return_value = MagicMock(
        choices=[choice], usage=usage,
    )

    from src.llm_providers.cerebras import CerebrasProvider

    prov = CerebrasProvider(api_key="k")
    result = prov.generate("sys", "user", {"type": "object"})

    assert result.parsed == {"ok": True}
    assert result.tokens_in == 100
    assert result.tokens_out == 50
    assert result.provider == "cerebras"
    # response_format is json_object (schema goes into the system prompt)
    _, kwargs = fake_client.chat.completions.create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}
