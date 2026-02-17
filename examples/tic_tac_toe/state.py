"""Tic-tac-toe game state."""

from dataclasses import dataclass, field
from enum import Enum, auto

from ludos import BaseGameState


class Player(Enum):
    X = "X"
    O = "O"


class GameMode(Enum):
    ONE_PLAYER = auto()
    TWO_PLAYER = auto()


class GameStatus(Enum):
    PLAYING = auto()
    X_WINS = auto()
    O_WINS = auto()
    DRAW = auto()


Board = list[list[Player | None]]

WIN_LINES = [
    # Rows
    [(0, 0), (0, 1), (0, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(2, 0), (2, 1), (2, 2)],
    # Columns
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    # Diagonals
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)],
]


def empty_board() -> Board:
    return [[None, None, None] for _ in range(3)]


def check_winner(board: Board) -> tuple[GameStatus, list[tuple[int, int]]]:
    """Check board for a winner or draw. Returns (status, winning_cells)."""
    for line in WIN_LINES:
        cells = [board[r][c] for r, c in line]
        if cells[0] is not None and cells[0] == cells[1] == cells[2]:
            status = GameStatus.X_WINS if cells[0] == Player.X else GameStatus.O_WINS
            return status, list(line)

    if all(board[r][c] is not None for r in range(3) for c in range(3)):
        return GameStatus.DRAW, []

    return GameStatus.PLAYING, []


@dataclass
class TicTacToeState(BaseGameState):
    board: Board = field(default_factory=empty_board)
    current_player: Player = Player.X
    status: GameStatus = GameStatus.PLAYING
    mode: GameMode = GameMode.ONE_PLAYER
    winning_cells: list[tuple[int, int]] = field(default_factory=list)
    ai_player: Player = Player.O
    ai_timer: float = 0.0
