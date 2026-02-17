# Ludos User Guide

Ludos is a pygame-ce abstraction framework that eliminates boilerplate and lets you build games fast. You define your state, scenes, and input bindings — Ludos handles the game loop, event conversion, and display management.

## Installation

```bash
# Clone and install with uv
uv sync --all-extras
```

**Requirements**: Python >= 3.12, pygame-ce >= 2.5.0

## Quickstart

Here is the smallest possible Ludos program — a window with a menu:

```python
from ludos import GameEngine, EngineConfig, MenuScene, MenuItem, MenuConfig


def on_start():
    print("Starting!")


def on_quit():
    print("Goodbye!")


engine = GameEngine(
    config=EngineConfig(title="My Game", width=800, height=600, fps=60),
    initial_scene=MenuScene(
        items=[
            MenuItem("Start Game", on_start),
            MenuItem("Quit", on_quit),
        ],
        config=MenuConfig(title="Main Menu"),
    ),
)
engine.run()
```

This opens an 800x600 window with a navigable menu. Arrow keys move the selection, Enter confirms. The window closes when you press the X button.

## Core Concepts

Ludos's architecture separates concerns into four systems:

```
GameEngine (composition root)
    ├── Window           — pygame display surface
    ├── InputHandler     — polls events, resolves semantic actions
    │   └── KeyBindings  — key/button → action mapping
    ├── SceneManager     — stack-based scene switching
    │   └── BaseScene    — your game screens (ABC)
    └── StateManager[T]  — generic over your state dataclass
```

The game loop runs **Input → Update → Render** every frame with delta time.

## State

### Defining State

Extend `BaseGameState` with a `@dataclass`. Your fields sit alongside the built-in ones:

```python
from dataclasses import dataclass
from ludos import BaseGameState


@dataclass
class MyState(BaseGameState):
    score: int = 0
    player_x: float = 400.0
    player_y: float = 300.0
    lives: int = 3
```

**Built-in fields** (managed by the engine):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_running` | `bool` | `True` | Set to `False` to stop the engine |
| `frame_count` | `int` | `0` | Incremented each frame by the engine |
| `elapsed_time` | `float` | `0.0` | Total seconds elapsed |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary storage for your own use |

### Mutating State

State is managed through `StateManager[T]`. Mutations use an explicit mutator pattern:

```python
# Inside a scene's handle_input or update:
engine.state_manager.update(lambda s: setattr(s, "score", s.score + 10))
```

The `StateManager` tracks whether state has changed via a `dirty` flag, which the engine resets after each render frame with `mark_clean()`.

### StateManager API

| Member | Type | Description |
|--------|------|-------------|
| `state` | property → `T` | The current state instance |
| `dirty` | property → `bool` | `True` if state was mutated since last `mark_clean()` |
| `update(mutator)` | method | Apply a `Callable[[T], None]` to mutate state |
| `mark_clean()` | method | Reset the dirty flag |

If the mutator raises, it is wrapped in a `StateError`.

## Input

### InputEvent

Raw pygame events are converted to `InputEvent` — a frozen dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `type` | `InputType` | Event category (see below) |
| `key` | `int \| None` | Pygame key constant (keyboard events) |
| `button` | `int \| None` | Mouse button number (mouse events) |
| `pos` | `tuple[int, int] \| None` | Mouse position (mouse events) |
| `action` | `str \| None` | Semantic action resolved from KeyBindings |

### InputType

```python
from ludos import InputType

InputType.KEY_DOWN      # Key pressed
InputType.KEY_UP        # Key released
InputType.MOUSE_DOWN    # Mouse button pressed
InputType.MOUSE_UP      # Mouse button released
InputType.MOUSE_MOTION  # Mouse moved
InputType.QUIT          # Window close
```

### KeyBindings

Maps raw pygame keys/buttons to semantic action strings. The engine uses these to populate `InputEvent.action`.

```python
from ludos import KeyBindings
import pygame

# Start from defaults or empty
bindings = KeyBindings.defaults()

# Add/override bindings
bindings.bind_key(pygame.K_w, "move_up")
bindings.bind_key(pygame.K_s, "move_down")
bindings.bind_mouse(2, "middle_click")

# Remove a binding
bindings.unbind_key(pygame.K_SPACE)

# Look up
bindings.get_key_action(pygame.K_w)     # "move_up"
bindings.get_mouse_action(1)            # "click"
```

**Default bindings** (`KeyBindings.defaults()`):

| Key/Button | Action |
|------------|--------|
| `K_UP` | `"move_up"` |
| `K_DOWN` | `"move_down"` |
| `K_LEFT` | `"move_left"` |
| `K_RIGHT` | `"move_right"` |
| `K_RETURN` | `"confirm"` |
| `K_ESCAPE` | `"cancel"` |
| `K_SPACE` | `"action"` |
| Mouse button 1 | `"click"` |
| Mouse button 3 | `"right_click"` |

### InputHandler

Polls pygame events, converts them to `InputEvent`, and dispatches registered callbacks.

```python
from ludos import InputHandler, KeyBindings

handler = InputHandler(KeyBindings.defaults())

# Register callbacks for semantic actions
handler.on("confirm", lambda event: print("Confirmed!"))
handler.on("cancel", lambda event: print("Cancelled!"))

# Unregister
handler.off("confirm", my_callback)
```

You typically don't call `handler.poll()` yourself — the engine does it. But in your scenes, you receive the already-converted `InputEvent` objects.

## Scenes

### BaseScene

All game screens extend `BaseScene` and implement three required methods:

```python
import pygame
from ludos import BaseScene, BaseGameState, InputEvent, InputType


class GameplayScene(BaseScene):
    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        """Called once per input event per frame."""
        if event.action == "move_up":
            state.metadata["player_y"] = state.metadata.get("player_y", 300) - 5

    def update(self, dt: float, state: BaseGameState) -> None:
        """Called once per frame. dt = seconds since last frame."""
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        """Draw to the surface each frame."""
        surface.fill((30, 30, 60))

    # Optional lifecycle hooks:
    def on_enter(self, state: BaseGameState) -> None:
        """Called when this scene becomes active (pushed or uncovered)."""
        print("Entered gameplay!")

    def on_exit(self, state: BaseGameState) -> None:
        """Called when this scene is deactivated (popped or covered)."""
        print("Left gameplay!")
```

#### Input Repeat Delay

Set `input_repeat_delay` (seconds) on a scene class to throttle repeated `KEY_DOWN` events with a resolved action. This prevents held keys from firing too fast (e.g. menu navigation). Only `KEY_DOWN` events with a resolved action are throttled — mouse events, key-up events, and events without an action always pass through.

```python
class SlowMenuScene(BaseScene):
    input_repeat_delay = 0.2  # 200ms between repeated actions
```

Default is `0.0` (no throttling). Timestamps reset when the active scene changes.

### SceneManager

Scenes live on a stack. The topmost scene is the **active** scene that receives input, updates, and renders.

```python
from ludos import SceneManager, BaseGameState

manager = SceneManager()
state = BaseGameState()

manager.push(gameplay_scene, state)   # gameplay is active, on_enter called
manager.push(pause_scene, state)      # gameplay.on_exit → pause.on_enter
manager.pop(state)                    # pause.on_exit → gameplay.on_enter
manager.replace(menu_scene, state)    # gameplay.on_exit → menu.on_enter

manager.active   # The topmost scene (or None)
manager.depth    # Number of scenes on stack
manager.clear(state)  # Pop all scenes, calling on_exit for each
```

**Lifecycle flow**:
- `push(scene)`: old scene's `on_exit` → new scene's `on_enter`
- `pop()`: active scene's `on_exit` → uncovered scene's `on_enter`
- `replace(scene)`: old scene's `on_exit` → new scene's `on_enter`
- `clear()`: all scenes get `on_exit` called, stack empties

### MenuScene

A ready-made scene with keyboard-navigable menu items:

```python
from ludos import MenuScene, MenuItem, MenuConfig


def start_game():
    print("Starting!")


menu = MenuScene(
    items=[
        MenuItem("New Game", start_game),
        MenuItem("Options", lambda: print("Options")),
        MenuItem("Quit", lambda: print("Quit")),
    ],
    config=MenuConfig(
        title="My Game",
        font_size=36,
        font_name=None,             # None = pygame default font
        text_color=(255, 255, 255),
        highlight_color=(255, 255, 0),
        bg_color=(0, 0, 0),
        title_font_size=48,
        item_spacing=10,
    ),
)
```

Navigation uses the `"move_up"`, `"move_down"`, and `"confirm"` actions from your key bindings. Selection wraps around. `MenuScene` sets `input_repeat_delay = 0.15` by default so held arrow keys don't cycle too fast.

**MenuConfig fields**:

| Field | Type | Default |
|-------|------|---------|
| `font_size` | `int` | `36` |
| `font_name` | `str \| None` | `None` (system default) |
| `text_color` | `tuple[int, int, int]` | `(255, 255, 255)` |
| `highlight_color` | `tuple[int, int, int]` | `(255, 255, 0)` |
| `bg_color` | `tuple[int, int, int]` | `(0, 0, 0)` |
| `title` | `str` | `""` |
| `title_font_size` | `int` | `48` |
| `item_spacing` | `int` | `10` |

## Engine

### EngineConfig

```python
from ludos import EngineConfig

config = EngineConfig(
    width=800,              # Window width (default: 800)
    height=600,             # Window height (default: 600)
    title="Ludos",         # Window title (default: "Ludos")
    fps=60,                 # Target frames per second (default: 60)
    bg_color=(0, 0, 0),     # Background clear color (default: black)
    display_flags=0,        # Pygame display flags (default: 0)
)
```

### GameEngine

The composition root that ties everything together:

```python
from ludos import GameEngine, EngineConfig, KeyBindings

engine = GameEngine(
    config=EngineConfig(title="My Game"),
    initial_state=MyState(),
    initial_scene=my_scene,
    bindings=KeyBindings.defaults(),  # optional, defaults are used if omitted
)

# Access subsystems
engine.state_manager    # StateManager[T]
engine.scene_manager    # SceneManager
engine.input_handler    # InputHandler
engine.window           # Window (None until run() is called)

# Run the game
engine.run()    # Blocks until game ends

# Stop from inside a scene or callback
engine.stop()   # Sets is_running = False, loop exits after current frame
```

**Game loop order** (each frame):
1. Tick clock, compute delta time
2. Increment `frame_count` and `elapsed_time`
3. **Input**: poll events, dispatch to active scene's `handle_input`
4. `QUIT` events automatically call `engine.stop()`
5. **Update**: call active scene's `update(dt, state)`
6. **Render**: clear window, call active scene's `render(surface, state)`, flip display
7. Mark state clean

## Error Handling

All framework errors inherit from `LudosError`:

```python
from ludos import LudosError

try:
    engine.run()
except LudosError as e:
    print(f"Framework error: {e}")
```

| Error | Raised when |
|-------|-------------|
| `LudosError` | Base class for all errors |
| `InitializationError` | Pygame init or window creation fails |
| `StateError` | State mutator raises or invalid state passed |
| `SceneError` | Invalid scene operation (pop empty stack, push non-scene) |
| `InputError` | Invalid key binding (empty action string) |
| `RenderError` | Display flip fails |

## Complete Example

A game with a main menu that transitions to a gameplay scene:

```python
from dataclasses import dataclass

import pygame

from ludos import (
    BaseGameState,
    BaseScene,
    EngineConfig,
    GameEngine,
    InputEvent,
    KeyBindings,
    MenuConfig,
    MenuItem,
    MenuScene,
)


@dataclass
class MyState(BaseGameState):
    score: int = 0
    player_x: float = 400.0
    player_y: float = 300.0


class GameplayScene(BaseScene):
    def __init__(self, engine: GameEngine) -> None:
        self._engine = engine

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        if event.action == "cancel":
            # Return to menu
            self._engine.scene_manager.pop(state)
        elif event.action == "move_up":
            state.metadata["player_y"] = state.metadata.get("player_y", 300.0) - 5
        elif event.action == "move_down":
            state.metadata["player_y"] = state.metadata.get("player_y", 300.0) + 5
        elif event.action == "move_left":
            state.metadata["player_x"] = state.metadata.get("player_x", 400.0) - 5
        elif event.action == "move_right":
            state.metadata["player_x"] = state.metadata.get("player_x", 400.0) + 5

    def update(self, dt: float, state: BaseGameState) -> None:
        pass

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        surface.fill((20, 20, 40))
        x = int(state.metadata.get("player_x", 400.0))
        y = int(state.metadata.get("player_y", 300.0))
        pygame.draw.circle(surface, (0, 200, 255), (x, y), 20)


def main():
    bindings = KeyBindings.defaults()
    bindings.bind_key(pygame.K_w, "move_up")
    bindings.bind_key(pygame.K_s, "move_down")
    bindings.bind_key(pygame.K_a, "move_left")
    bindings.bind_key(pygame.K_d, "move_right")

    engine = GameEngine(
        config=EngineConfig(title="My Game", width=800, height=600),
        initial_state=MyState(),
        bindings=bindings,
    )

    gameplay = GameplayScene(engine)

    menu = MenuScene(
        items=[
            MenuItem("Play", lambda: engine.scene_manager.push(gameplay, engine.state_manager.state)),
            MenuItem("Quit", engine.stop),
        ],
        config=MenuConfig(title="My Game"),
    )

    engine._initial_scene = menu
    engine.run()


if __name__ == "__main__":
    main()
```

## Testing Your Game

Ludos is designed for testability. Mock pygame to test scenes without a display:

```python
from unittest.mock import MagicMock

from ludos import InputEvent, InputType
from your_game import GameplayScene, MyState


def test_move_up():
    scene = GameplayScene(engine=MagicMock())
    state = MyState()
    state.metadata["player_y"] = 300.0

    event = InputEvent(type=InputType.KEY_DOWN, action="move_up")
    scene.handle_input(event, state)

    assert state.metadata["player_y"] == 295.0
```

Run tests with:

```bash
uv run pytest
uv run pytest --cov=ludos
```
