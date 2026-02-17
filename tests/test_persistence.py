"""Tests for the save/load persistence system."""

from __future__ import annotations

import enum
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from ludos import BaseGameState, save_state, load_state, PersistenceError
from ludos.persistence import SAVE_VERSION, SKIP_FIELDS


# ---------------------------------------------------------------------------
# Test fixtures: state classes
# ---------------------------------------------------------------------------

class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Direction(enum.Enum):
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"


@dataclass
class Position:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Inventory:
    items: list[str] = field(default_factory=list)
    capacity: int = 10


@dataclass
class SimpleState(BaseGameState):
    score: int = 0
    name: str = "player"


@dataclass
class EnumState(BaseGameState):
    color: Color = Color.RED
    direction: Direction = Direction.NORTH


@dataclass
class SetState(BaseGameState):
    tags: set[str] = field(default_factory=set)
    colors: set[Color] = field(default_factory=set)
    empty: set[str] = field(default_factory=set)


@dataclass
class DictEnumKeyState(BaseGameState):
    scores: dict[Color, int] = field(default_factory=dict)
    labels: dict[Direction, str | None] = field(default_factory=dict)


@dataclass
class NestedState(BaseGameState):
    pos: Position = field(default_factory=Position)
    inventory: Inventory = field(default_factory=Inventory)


@dataclass
class DeeplyNestedState(BaseGameState):
    nested: NestedState = field(default_factory=NestedState)


@dataclass
class ListOfDataclassState(BaseGameState):
    positions: list[Position] = field(default_factory=list)


@dataclass
class OptionalState(BaseGameState):
    label: str | None = None
    value: int | None = None


@dataclass
class TupleState(BaseGameState):
    coords: tuple[int, int] = (0, 0)


@dataclass
class FrozensetState(BaseGameState):
    ids: frozenset[str] = field(default_factory=frozenset)


@dataclass
class ComplexState(BaseGameState):
    """Mimics a DungeonQuest-like state with all type combinations."""
    player_name: str = "Hero"
    level: int = 1
    hp: float = 100.0
    position: Position = field(default_factory=Position)
    inventory: Inventory = field(default_factory=Inventory)
    visited: set[str] = field(default_factory=set)
    color_scores: dict[Color, int] = field(default_factory=dict)
    facing: Direction = Direction.NORTH
    allies: list[str] = field(default_factory=list)
    flags: dict[str, bool] = field(default_factory=dict)
    active_color: Color | None = None


# ---------------------------------------------------------------------------
# TestSaveStateBasic
# ---------------------------------------------------------------------------

class TestSaveStateBasic:
    def test_creates_file(self, tmp_path: Path):
        state = SimpleState(score=42)
        path = tmp_path / "save.json"
        save_state(state, path)
        assert path.exists()

    def test_creates_parent_dirs(self, tmp_path: Path):
        path = tmp_path / "sub" / "dir" / "save.json"
        save_state(SimpleState(), path)
        assert path.exists()

    def test_produces_valid_json(self, tmp_path: Path):
        path = tmp_path / "save.json"
        save_state(SimpleState(score=10), path)
        data = json.loads(path.read_text())
        assert isinstance(data, dict)

    def test_engine_fields_excluded(self, tmp_path: Path):
        state = SimpleState(score=5)
        state.is_running = False
        state.frame_count = 999
        state.elapsed_time = 42.5
        path = tmp_path / "save.json"
        save_state(state, path)
        data = json.loads(path.read_text())
        for name in SKIP_FIELDS:
            assert name not in data

    def test_has_type_marker(self, tmp_path: Path):
        path = tmp_path / "save.json"
        save_state(SimpleState(), path)
        data = json.loads(path.read_text())
        assert data["__type__"] == "SimpleState"

    def test_has_save_version(self, tmp_path: Path):
        path = tmp_path / "save.json"
        save_state(SimpleState(), path)
        data = json.loads(path.read_text())
        assert data["__save_version__"] == SAVE_VERSION

    def test_rejects_non_state(self, tmp_path: Path):
        with pytest.raises(PersistenceError, match="Expected a BaseGameState"):
            save_state("not a state", tmp_path / "save.json")


# ---------------------------------------------------------------------------
# TestLoadStateBasic
# ---------------------------------------------------------------------------

class TestLoadStateBasic:
    def test_round_trip(self, tmp_path: Path):
        original = SimpleState(score=42, name="hero")
        path = tmp_path / "save.json"
        save_state(original, path)
        loaded = load_state(SimpleState, path)
        assert loaded.score == 42
        assert loaded.name == "hero"

    def test_engine_fields_restored_to_defaults(self, tmp_path: Path):
        state = SimpleState(score=1)
        state.frame_count = 500
        state.elapsed_time = 99.9
        state.is_running = False
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(SimpleState, path)
        assert loaded.is_running is True
        assert loaded.frame_count == 0
        assert loaded.elapsed_time == 0.0

    def test_missing_file(self, tmp_path: Path):
        with pytest.raises(PersistenceError, match="Save file not found"):
            load_state(SimpleState, tmp_path / "nope.json")

    def test_invalid_json(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("{invalid json!!!")
        with pytest.raises(PersistenceError, match="Invalid JSON"):
            load_state(SimpleState, path)

    def test_wrong_version(self, tmp_path: Path):
        path = tmp_path / "save.json"
        path.write_text(json.dumps({"__save_version__": 999}))
        with pytest.raises(PersistenceError, match="Unsupported save version"):
            load_state(SimpleState, path)

    def test_missing_version(self, tmp_path: Path):
        path = tmp_path / "save.json"
        path.write_text(json.dumps({"score": 1}))
        with pytest.raises(PersistenceError, match="Unsupported save version"):
            load_state(SimpleState, path)


# ---------------------------------------------------------------------------
# TestEnumSerialization
# ---------------------------------------------------------------------------

class TestEnumSerialization:
    def test_enum_round_trip(self, tmp_path: Path):
        state = EnumState(color=Color.BLUE, direction=Direction.WEST)
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(EnumState, path)
        assert loaded.color is Color.BLUE
        assert loaded.direction is Direction.WEST

    def test_enum_serialized_format(self, tmp_path: Path):
        state = EnumState(color=Color.GREEN)
        path = tmp_path / "save.json"
        save_state(state, path)
        data = json.loads(path.read_text())
        assert data["color"] == {"__enum__": "Color.GREEN"}


# ---------------------------------------------------------------------------
# TestSetSerialization
# ---------------------------------------------------------------------------

class TestSetSerialization:
    def test_string_set_round_trip(self, tmp_path: Path):
        state = SetState(tags={"a", "b", "c"})
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(SetState, path)
        assert loaded.tags == {"a", "b", "c"}

    def test_enum_set_round_trip(self, tmp_path: Path):
        state = SetState(colors={Color.RED, Color.BLUE})
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(SetState, path)
        assert loaded.colors == {Color.RED, Color.BLUE}

    def test_empty_set_round_trip(self, tmp_path: Path):
        state = SetState()
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(SetState, path)
        assert loaded.empty == set()


# ---------------------------------------------------------------------------
# TestDictWithEnumKeys
# ---------------------------------------------------------------------------

class TestDictWithEnumKeys:
    def test_enum_key_round_trip(self, tmp_path: Path):
        state = DictEnumKeyState(scores={Color.RED: 10, Color.BLUE: 20})
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(DictEnumKeyState, path)
        assert loaded.scores == {Color.RED: 10, Color.BLUE: 20}

    def test_none_values(self, tmp_path: Path):
        state = DictEnumKeyState(
            labels={Direction.NORTH: "up", Direction.SOUTH: None}
        )
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(DictEnumKeyState, path)
        assert loaded.labels[Direction.NORTH] == "up"
        assert loaded.labels[Direction.SOUTH] is None

    def test_enum_key_serialized_as_name(self, tmp_path: Path):
        state = DictEnumKeyState(scores={Color.RED: 5})
        path = tmp_path / "save.json"
        save_state(state, path)
        data = json.loads(path.read_text())
        assert "RED" in data["scores"]


# ---------------------------------------------------------------------------
# TestNestedDataclasses
# ---------------------------------------------------------------------------

class TestNestedDataclasses:
    def test_nested_round_trip(self, tmp_path: Path):
        state = NestedState(
            pos=Position(10.5, 20.3),
            inventory=Inventory(items=["sword", "potion"], capacity=5),
        )
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(NestedState, path)
        assert loaded.pos.x == 10.5
        assert loaded.pos.y == 20.3
        assert loaded.inventory.items == ["sword", "potion"]
        assert loaded.inventory.capacity == 5

    def test_deeply_nested_round_trip(self, tmp_path: Path):
        inner = NestedState(pos=Position(1.0, 2.0))
        state = DeeplyNestedState(nested=inner)
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(DeeplyNestedState, path)
        assert loaded.nested.pos.x == 1.0

    def test_list_of_dataclasses(self, tmp_path: Path):
        state = ListOfDataclassState(
            positions=[Position(1, 2), Position(3, 4)]
        )
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(ListOfDataclassState, path)
        assert len(loaded.positions) == 2
        assert loaded.positions[0].x == 1
        assert loaded.positions[1].y == 4


# ---------------------------------------------------------------------------
# TestComplexStateTree
# ---------------------------------------------------------------------------

class TestComplexStateTree:
    def test_complex_round_trip(self, tmp_path: Path):
        state = ComplexState(
            player_name="Gandalf",
            level=5,
            hp=75.5,
            position=Position(10, 20),
            inventory=Inventory(items=["staff", "ring"], capacity=20),
            visited={"cave", "forest", "town"},
            color_scores={Color.RED: 100, Color.GREEN: 50},
            facing=Direction.EAST,
            allies=["Frodo", "Sam"],
            flags={"quest_started": True, "boss_defeated": False},
            active_color=Color.BLUE,
        )
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(ComplexState, path)

        assert loaded.player_name == "Gandalf"
        assert loaded.level == 5
        assert loaded.hp == 75.5
        assert loaded.position.x == 10
        assert loaded.position.y == 20
        assert loaded.inventory.items == ["staff", "ring"]
        assert loaded.inventory.capacity == 20
        assert loaded.visited == {"cave", "forest", "town"}
        assert loaded.color_scores == {Color.RED: 100, Color.GREEN: 50}
        assert loaded.facing is Direction.EAST
        assert loaded.allies == ["Frodo", "Sam"]
        assert loaded.flags == {"quest_started": True, "boss_defeated": False}
        assert loaded.active_color is Color.BLUE


# ---------------------------------------------------------------------------
# TestOptionalFields
# ---------------------------------------------------------------------------

class TestOptionalFields:
    def test_none_round_trip(self, tmp_path: Path):
        state = OptionalState(label=None, value=None)
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(OptionalState, path)
        assert loaded.label is None
        assert loaded.value is None

    def test_some_round_trip(self, tmp_path: Path):
        state = OptionalState(label="hello", value=42)
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(OptionalState, path)
        assert loaded.label == "hello"
        assert loaded.value == 42


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_state(self, tmp_path: Path):
        state = BaseGameState()
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(BaseGameState, path)
        assert loaded.metadata == {}

    def test_metadata_dict(self, tmp_path: Path):
        state = BaseGameState()
        state.metadata = {"key": "value", "num": 42}
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(BaseGameState, path)
        assert loaded.metadata == {"key": "value", "num": 42}

    def test_tuple_round_trip(self, tmp_path: Path):
        state = TupleState(coords=(5, 10))
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(TupleState, path)
        assert loaded.coords == (5, 10)

    def test_frozenset_round_trip(self, tmp_path: Path):
        state = FrozensetState(ids=frozenset(["a", "b", "c"]))
        path = tmp_path / "save.json"
        save_state(state, path)
        loaded = load_state(FrozensetState, path)
        assert loaded.ids == frozenset(["a", "b", "c"])
        assert isinstance(loaded.ids, frozenset)

    def test_string_path(self, tmp_path: Path):
        path = str(tmp_path / "save.json")
        save_state(SimpleState(score=1), path)
        loaded = load_state(SimpleState, path)
        assert loaded.score == 1
