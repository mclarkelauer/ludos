"""Rendering utilities for tic-tac-toe."""

import pygame

from examples.tic_tac_toe.state import Board, Player, GameStatus

# Layout constants
GRID_SIZE = 450
CELL_SIZE = GRID_SIZE // 3
GRID_X = 75  # (600 - 450) / 2
GRID_Y = 120
LINE_WIDTH = 4
MARK_PADDING = 25

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
DARK_BG = (30, 30, 40)


def pos_to_cell(pos: tuple[int, int]) -> tuple[int, int] | None:
    """Convert pixel position to grid (row, col), or None if outside grid."""
    x, y = pos
    if x < GRID_X or x >= GRID_X + GRID_SIZE:
        return None
    if y < GRID_Y or y >= GRID_Y + GRID_SIZE:
        return None
    col = (x - GRID_X) // CELL_SIZE
    row = (y - GRID_Y) // CELL_SIZE
    return (row, col)


def draw_grid(surface: pygame.Surface) -> None:
    """Draw the 3x3 grid lines."""
    for i in range(1, 3):
        # Vertical
        x = GRID_X + i * CELL_SIZE
        pygame.draw.line(surface, GRAY, (x, GRID_Y), (x, GRID_Y + GRID_SIZE), LINE_WIDTH)
        # Horizontal
        y = GRID_Y + i * CELL_SIZE
        pygame.draw.line(surface, GRAY, (GRID_X, y), (GRID_X + GRID_SIZE, y), LINE_WIDTH)


def draw_x(surface: pygame.Surface, row: int, col: int, color: tuple[int, int, int] = RED) -> None:
    """Draw an X mark in the given cell."""
    x1 = GRID_X + col * CELL_SIZE + MARK_PADDING
    y1 = GRID_Y + row * CELL_SIZE + MARK_PADDING
    x2 = GRID_X + (col + 1) * CELL_SIZE - MARK_PADDING
    y2 = GRID_Y + (row + 1) * CELL_SIZE - MARK_PADDING
    pygame.draw.line(surface, color, (x1, y1), (x2, y2), LINE_WIDTH + 2)
    pygame.draw.line(surface, color, (x2, y1), (x1, y2), LINE_WIDTH + 2)


def draw_o(surface: pygame.Surface, row: int, col: int, color: tuple[int, int, int] = BLUE) -> None:
    """Draw an O mark in the given cell."""
    cx = GRID_X + col * CELL_SIZE + CELL_SIZE // 2
    cy = GRID_Y + row * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2 - MARK_PADDING
    pygame.draw.circle(surface, color, (cx, cy), radius, LINE_WIDTH + 2)


def draw_board(surface: pygame.Surface, board: Board, winning_cells: list[tuple[int, int]]) -> None:
    """Draw all marks on the board with winning highlight."""
    for r in range(3):
        for c in range(3):
            cell = board[r][c]
            if cell is None:
                continue
            is_winner = (r, c) in winning_cells
            if cell == Player.X:
                draw_x(surface, r, c, YELLOW if is_winner else RED)
            else:
                draw_o(surface, r, c, YELLOW if is_winner else BLUE)


def draw_status(surface: pygame.Surface, status: GameStatus, current_player: Player) -> None:
    """Draw status text above the grid."""
    font = pygame.font.Font(None, 40)
    if status == GameStatus.PLAYING:
        text = f"Player {current_player.value}'s turn"
    elif status == GameStatus.X_WINS:
        text = "X wins!"
    elif status == GameStatus.O_WINS:
        text = "O wins!"
    else:
        text = "Draw!"
    rendered = font.render(text, True, WHITE)
    rect = rendered.get_rect(center=(surface.get_width() // 2, 50))
    surface.blit(rendered, rect)


def draw_instructions(surface: pygame.Surface, status: GameStatus) -> None:
    """Draw instruction text below the grid."""
    font = pygame.font.Font(None, 28)
    if status == GameStatus.PLAYING:
        text = "Click a cell to play  |  ESC = menu"
    else:
        text = "Click anywhere to return to menu"
    rendered = font.render(text, True, GRAY)
    rect = rendered.get_rect(center=(surface.get_width() // 2, GRID_Y + GRID_SIZE + 50))
    surface.blit(rendered, rect)
