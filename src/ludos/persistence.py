"""JSON-based save/load for game state."""

from __future__ import annotations

import dataclasses
import enum
import json
import sys
import typing
from pathlib import Path
from typing import TypeVar

from ludos.errors import PersistenceError
from ludos.state.base import BaseGameState

T = TypeVar("T", bound=BaseGameState)

SAVE_VERSION = 1

SKIP_FIELDS: frozenset[str] = frozenset({"is_running", "frame_count", "elapsed_time"})


def save_state(state: BaseGameState, path: str | Path) -> None:
    """Serialize game state to a JSON file.

    Fields managed by the engine (is_running, frame_count, elapsed_time)
    are excluded from the save.

    Args:
        state: The game state to save.
        path: Destination file path. Parent directories are created if needed.

    Raises:
        PersistenceError: If state is not a BaseGameState or writing fails.
    """
    if not isinstance(state, BaseGameState):
        raise PersistenceError(
            f"Expected a BaseGameState instance, got {type(state).__name__}"
        )
    try:
        data = _serialize(state)
        data["__save_version__"] = SAVE_VERSION
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    except PersistenceError:
        raise
    except Exception as exc:
        raise PersistenceError(f"Failed to save state: {exc}") from exc


def load_state(state_class: type[T], path: str | Path) -> T:
    """Deserialize game state from a JSON file.

    Engine-managed fields (is_running, frame_count, elapsed_time) are
    restored to their defaults regardless of what was saved.

    Args:
        state_class: The dataclass type to deserialize into.
        path: Source file path.

    Returns:
        A new instance of state_class populated from the file.

    Raises:
        PersistenceError: If the file is missing, contains invalid JSON,
            has a wrong save version, or deserialization fails.
    """
    p = Path(path)
    if not p.exists():
        raise PersistenceError(f"Save file not found: {path}")
    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise PersistenceError(f"Invalid JSON in save file: {exc}") from exc

    version = raw.pop("__save_version__", None)
    if version != SAVE_VERSION:
        raise PersistenceError(
            f"Unsupported save version {version!r}, expected {SAVE_VERSION}"
        )

    try:
        instance = _deserialize_dataclass(state_class, raw)
    except PersistenceError:
        raise
    except Exception as exc:
        raise PersistenceError(f"Failed to load state: {exc}") from exc

    # Reset engine-managed fields to defaults
    defaults = {f.name: f.default for f in dataclasses.fields(BaseGameState)
                if f.name in SKIP_FIELDS}
    for name, default in defaults.items():
        setattr(instance, name, default)

    return instance


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _serialize(obj: object) -> object:
    """Recursively serialize an object to JSON-compatible types."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, enum.Enum):
        return {"__enum__": f"{type(obj).__name__}.{obj.name}"}

    if isinstance(obj, (set, frozenset)):
        elements = [_serialize(e) for e in obj]
        # Sort for deterministic output when elements are comparable
        try:
            elements = sorted(elements, key=_sort_key)
        except TypeError:
            pass
        return {"__set__": elements}

    if isinstance(obj, tuple):
        return {"__tuple__": [_serialize(e) for e in obj]}

    if isinstance(obj, list):
        return [_serialize(e) for e in obj]

    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if isinstance(k, enum.Enum):
                key = k.name
            else:
                key = k
            result[key] = _serialize(v)
        return result

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        data: dict[str, object] = {"__type__": type(obj).__name__}
        for f in dataclasses.fields(obj):
            if f.name in SKIP_FIELDS:
                continue
            data[f.name] = _serialize(getattr(obj, f.name))
        return data

    # Fallback: let json handle it or fail
    return obj


def _sort_key(x: object) -> tuple:
    """Produce a sortable key for mixed-type serialized values."""
    if isinstance(x, dict) and "__enum__" in x:
        return (0, x["__enum__"])
    if isinstance(x, str):
        return (1, x)
    if isinstance(x, (int, float)):
        return (2, x)
    return (3, str(x))


# ---------------------------------------------------------------------------
# Deserialization helpers
# ---------------------------------------------------------------------------

def _resolve_type_hints(cls: type) -> dict[str, type]:
    """Get type hints for a class, resolving forward references."""
    module = sys.modules.get(cls.__module__, None)
    globalns = getattr(module, "__dict__", {}) if module else {}
    return typing.get_type_hints(cls, globalns=globalns)


def _resolve_enum(value: str, enum_type: type) -> enum.Enum:
    """Resolve 'ClassName.MEMBER' to an enum instance."""
    _, _, member_name = value.partition(".")
    return enum_type[member_name]


def _unwrap_optional(hint: type) -> tuple[type | None, bool]:
    """If hint is Optional[X] / X | None, return (X, True). Else (hint, False)."""
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and len(args) == 2:
            return non_none[0], True
    return hint, False


def _find_class_in_module(cls: type, name: str) -> type | None:
    """Find a class by name in the same module as cls, or in ludos modules."""
    module = sys.modules.get(cls.__module__)
    if module:
        result = getattr(module, name, None)
        if result is not None:
            return result

    # Search ludos modules
    for mod_name, mod in sys.modules.items():
        if mod_name.startswith("ludos") and mod is not None:
            result = getattr(mod, name, None)
            if isinstance(result, type):
                return result
    return None


def _deserialize_value(value: object, hint: type, context_cls: type) -> object:
    """Deserialize a JSON value into the expected Python type."""
    if value is None:
        return None

    # Unwrap Optional
    inner, is_optional = _unwrap_optional(hint)
    if is_optional:
        if value is None:
            return None
        return _deserialize_value(value, inner, context_cls)

    origin = typing.get_origin(inner)
    args = typing.get_args(inner)

    # Tagged enum
    if isinstance(value, dict) and "__enum__" in value:
        if isinstance(inner, type) and issubclass(inner, enum.Enum):
            return _resolve_enum(value["__enum__"], inner)
        # Try to find the enum class from the tag
        class_name = value["__enum__"].split(".")[0]
        enum_cls = _find_class_in_module(context_cls, class_name)
        if enum_cls and issubclass(enum_cls, enum.Enum):
            return _resolve_enum(value["__enum__"], enum_cls)
        raise PersistenceError(f"Cannot resolve enum type for {value}")

    # Tagged set/frozenset
    if isinstance(value, dict) and "__set__" in value:
        elements = value["__set__"]
        elem_hint = args[0] if args else str
        deserialized = [_deserialize_value(e, elem_hint, context_cls) for e in elements]
        if inner is frozenset or (origin is not None and origin is frozenset):
            return frozenset(deserialized)
        return set(deserialized)

    # Tagged tuple
    if isinstance(value, dict) and "__tuple__" in value:
        elements = value["__tuple__"]
        if args:
            return tuple(
                _deserialize_value(e, args[i % len(args)], context_cls)
                for i, e in enumerate(elements)
            )
        return tuple(elements)

    # Tagged nested dataclass
    if isinstance(value, dict) and "__type__" in value:
        type_name = value["__type__"]
        target_cls = _find_class_in_module(context_cls, type_name)
        if target_cls and dataclasses.is_dataclass(target_cls):
            return _deserialize_dataclass(target_cls, value)
        raise PersistenceError(f"Cannot resolve dataclass type {type_name!r}")

    # list
    if origin is list:
        elem_hint = args[0] if args else object
        return [_deserialize_value(e, elem_hint, context_cls) for e in value]

    # set / frozenset (untagged, from type hint)
    if origin in (set, frozenset):
        elem_hint = args[0] if args else object
        elems = value if isinstance(value, list) else value
        deserialized = [_deserialize_value(e, elem_hint, context_cls) for e in elems]
        if origin is frozenset:
            return frozenset(deserialized)
        return set(deserialized)

    # dict
    if origin is dict:
        key_hint = args[0] if args else str
        val_hint = args[1] if len(args) > 1 else object
        result = {}
        for k, v in value.items():
            # Dict keys that are enum types: stored as member name strings
            if isinstance(key_hint, type) and issubclass(key_hint, enum.Enum):
                k = key_hint[k]
            result[k] = _deserialize_value(v, val_hint, context_cls)
        return result

    # Dataclass hint (untagged)
    if isinstance(inner, type) and dataclasses.is_dataclass(inner) and isinstance(value, dict):
        return _deserialize_dataclass(inner, value)

    # Primitives pass through
    return value


def _deserialize_dataclass(cls: type[T], data: dict) -> T:
    """Reconstruct a dataclass instance from deserialized JSON data."""
    hints = _resolve_type_hints(cls)
    kwargs = {}
    # Remove the __type__ marker if present
    data = {k: v for k, v in data.items() if k != "__type__"}

    for f in dataclasses.fields(cls):
        if f.name in SKIP_FIELDS:
            continue
        if f.name in data:
            hint = hints.get(f.name, object)
            kwargs[f.name] = _deserialize_value(data[f.name], hint, cls)

    return cls(**kwargs)
