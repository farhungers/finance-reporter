"""Groq strict-schema transformer regression — 2026-08-18 root-cause fix.

Groq's `json_object` mode was accepting malformed output from gpt-oss-20b
(json_validate_failed × 3 on nested trade schema). Fix: switch to strict
`json_schema` mode with constrained decoding.

Groq strict-mode rules (per 2026-08 docs):
  1. `additionalProperties: false` on every object
  2. Every property listed in `required`
  3. Optional fields expressed as nullable via union type

_make_strict() transforms our schemas to satisfy these without mutating the
input (so other providers + tests keep working).
"""
from __future__ import annotations

from src.llm_providers.groq import _make_strict
from src.pitches import _PITCH_SCHEMA
from src.trades import _TRADE_SCHEMA


def test_object_gets_additional_properties_false():
    s = _make_strict({"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]})
    assert s["additionalProperties"] is False


def test_all_properties_moved_to_required():
    s = _make_strict({
        "type": "object",
        "properties": {"a": {"type": "string"}, "b": {"type": "number"}},
        "required": ["a"],
    })
    assert set(s["required"]) == {"a", "b"}


def test_nested_object_also_strictified():
    s = _make_strict({
        "type": "object",
        "properties": {
            "outer": {
                "type": "object",
                "properties": {"inner": {"type": "string"}},
            }
        },
    })
    assert s["additionalProperties"] is False
    assert s["properties"]["outer"]["additionalProperties"] is False
    assert s["properties"]["outer"]["required"] == ["inner"]


def test_array_items_strictified():
    s = _make_strict({
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"x": {"type": "integer"}},
                },
            }
        },
    })
    assert s["properties"]["items"]["items"]["additionalProperties"] is False
    assert s["properties"]["items"]["items"]["required"] == ["x"]


def test_input_not_mutated():
    inp = {"type": "object", "properties": {"a": {"type": "string"}}, "required": []}
    _ = _make_strict(inp)
    assert inp["required"] == []
    assert "additionalProperties" not in inp


def test_nullable_optional_field_becomes_union_type():
    # low_star_warning is in the _NULLABLE_KEYS set — model must be able to
    # emit null when the pitch's stars≥2 and no warning needs shipping.
    s = _make_strict({
        "type": "object",
        "properties": {
            "low_star_warning": {"type": "string"},
        },
    })
    assert s["properties"]["low_star_warning"]["type"] == ["string", "null"]
    assert "low_star_warning" in s["required"]


def test_real_pitch_schema_strictifies_cleanly():
    s = _make_strict(_PITCH_SCHEMA)
    assert s["additionalProperties"] is False
    pitches_arr = s["properties"]["pitches"]
    assert pitches_arr["type"] == "array"
    item = pitches_arr["items"]
    assert item["additionalProperties"] is False
    # Every original property must now be required
    orig_props = _PITCH_SCHEMA["properties"]["pitches"]["items"]["properties"]
    assert set(item["required"]) == set(orig_props.keys())
    # Nested rubric object also strictified
    assert item["properties"]["rubric"]["additionalProperties"] is False


def test_real_trade_schema_strictifies_cleanly():
    s = _make_strict(_TRADE_SCHEMA)
    assert s["additionalProperties"] is False
    for klass in ("commodity", "equity", "crypto"):
        item = s["properties"][klass]
        assert item["additionalProperties"] is False
        assert item["properties"]["rubric"]["additionalProperties"] is False
