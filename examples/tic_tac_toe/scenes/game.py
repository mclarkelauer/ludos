"""Game scene for tic-tac-toe."""

import pygame

from ludos import BaseScene, BaseGameState
from ludos.input.events import InputEvent, InputType

from examples.tic_tac_toe.ai import best_move
from examples.tic_tac_toe.rendering import (
    DARK_BG,
    draw_board,
    draw_grid,
    draw_instructions,
    draw_status,
    pos_to_cell,
)
from examples.tic_tac_toe.state import (
    GameMode,
    GameStatus,
    Player,
    TicTacToeState,
    check_winner,
    empty_board,
)

AI_DELAY = 0.4


class GameScene(BaseScene):
    """Handles gameplay and game-over display."""

    def __init__(self, engine, mode: GameMode) -> None:
        self._engine = engine
        self._mode = mode

    def on_enter(self, state: BaseGameState) -> None:
        ttt = self._ttt(state)
        ttt.board = empty_board()
        ttt.current_player = Player.X
        ttt.status = GameStatus.PLAYING
        ttt.mode = self._mode
        ttt.winning_cells = []
        ttt.ai_timer = 0.0

    def handle_input(self, event: InputEvent, state: BaseGameState) -> None:
        ttt = self._ttt(state)

        if event.action == "cancel":
            self._return_to_menu(ttt)
            return

        if event.type != InputType.MOUSE_DOWN or event.action != "click":
            return

        if ttt.status != GameStatus.PLAYING:
            self._return_to_menu(ttt)
            return

        if ttt.mode == GameMode.ONE_PLAYER and ttt.current_player == ttt.ai_player:
            return

        if event.pos is None:
            return

        cell = pos_to_cell(event.pos)
        if cell is None:
            return

        row, col = cell
        if ttt.board[row][col] is not None:
            return

        self._place(ttt, row, col)

    def update(self, dt: float, state: BaseGameState) -> None:
        ttt = self._ttt(state)
        if (
            ttt.status == GameStatus.PLAYING
            and ttt.mode == GameMode.ONE_PLAYER
            and ttt.current_player == ttt.ai_player
        ):
            ttt.ai_timer += dt
            if ttt.ai_timer >= AI_DELAY:
                move = best_move(ttt.board, ttt.ai_player)
                if move:
                    self._place(ttt, *move)

    def render(self, surface: pygame.Surface, state: BaseGameState) -> None:
        ttt = self._ttt(state)
        surface.fill(DARK_BG)
        draw_status(surface, ttt.status, ttt.current_player)
        draw_grid(surface)
        draw_board(surface, ttt.board, ttt.winning_cells)
        draw_instructions(surface, ttt.status)

    def _ttt(self, state: BaseGameState) -> TicTacToeState:
        assert isinstance(state, TicTacToeState)
        return state

    def _place(self, ttt: TicTacToeState, row: int, col: int) -> None:
        ttt.board[row][col] = ttt.current_player
        status, cells = check_winner(ttt.board)
        ttt.status = status
        ttt.winning_cells = cells
        if status == GameStatus.PLAYING:
            ttt.current_player = Player.O if ttt.current_player == Player.X else Player.X
            ttt.ai_timer = 0.0

    def _return_to_menu(self, ttt: TicTacToeState) -> None:
        self._engine.scene_manager.pop(ttt)
