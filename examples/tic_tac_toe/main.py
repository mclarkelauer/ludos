"""Tic-tac-toe example using the Ludos framework."""

from ludos import EngineConfig, GameEngine, MenuConfig, MenuItem, MenuScene

from examples.tic_tac_toe.scenes.game import GameScene
from examples.tic_tac_toe.state import GameMode, TicTacToeState


def main() -> None:
    engine = GameEngine(
        config=EngineConfig(
            width=600,
            height=700,
            title="Tic-Tac-Toe",
            bg_color=(30, 30, 40),
        ),
        initial_state=TicTacToeState(),
    )

    def start_1p() -> None:
        scene = GameScene(engine, GameMode.ONE_PLAYER)
        engine.scene_manager.push(scene, engine.state_manager.state)

    def start_2p() -> None:
        scene = GameScene(engine, GameMode.TWO_PLAYER)
        engine.scene_manager.push(scene, engine.state_manager.state)

    menu = MenuScene(
        items=[
            MenuItem("1 Player", start_1p),
            MenuItem("2 Players", start_2p),
            MenuItem("Quit", engine.stop),
        ],
        config=MenuConfig(
            title="Tic-Tac-Toe",
            title_font_size=56,
            font_size=40,
            bg_color=(30, 30, 40),
        ),
    )

    engine._initial_scene = menu
    engine.run()


if __name__ == "__main__":
    main()
