# Ludos

Pygame-ce abstraction framework that eliminates boilerplate for rapid game development. Clean separation between input, state, and rendering with extensibility at every layer.

## Install

```bash
pip install ludos
```

## Quick Start

```python
from dataclasses import dataclass
import pygame
from ludos import (
    BaseGameState, BaseScene, EngineConfig, GameEngine,
    KeyBindings, SceneManager, StateManager,
)

@dataclass
class MyState(BaseGameState):
    score: int = 0

class PlayScene(BaseScene):
    def handle_input(self, events, state_manager):
        pass

    def update(self, dt, state_manager):
        pass

    def render(self, surface, state_manager):
        surface.fill((0, 0, 0))

config = EngineConfig(title="My Game", width=800, height=600)
state_manager = StateManager(MyState())
scene_manager = SceneManager()
scene_manager.push(PlayScene())

engine = GameEngine(config)
engine.run(scene_manager, state_manager)
```

## Features

- **State management** — Subclass `BaseGameState` as a dataclass, mutate through `StateManager.update()`
- **Scene stack** — Push/pop/replace scenes with `on_enter`/`on_exit` lifecycle hooks
- **Input mapping** — Map raw pygame keys to semantic actions via `KeyBindings`
- **Display wrapper** — `Window` handles pygame display init and surface management
- **Built-in menu** — `MenuScene` with configurable `MenuConfig` for quick prototyping
- **Error hierarchy** — All errors inherit `LudosError` for unified catching

## Documentation

See the [user guide](docs/guide.md) for full documentation.

## License

MIT
