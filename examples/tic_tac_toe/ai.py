"""Minimax AI for tic-tac-toe."""

from examples.tic_tac_toe.state import Board, Player, check_winner, GameStatus


def _opponent(player: Player) -> Player:
    return Player.O if player == Player.X else Player.X


def minimax(board: Board, is_maximizing: bool, ai: Player, depth: int = 0) -> int:
    """Return score for the current board position."""
    status, _ = check_winner(board)
    if status == GameStatus.X_WINS:
        return (10 - depth) if ai == Player.X else -(10 - depth)
    if status == GameStatus.O_WINS:
        return (10 - depth) if ai == Player.O else -(10 - depth)
    if status == GameStatus.DRAW:
        return 0

    if is_maximizing:
        best = -100
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = ai
                    best = max(best, minimax(board, False, ai, depth + 1))
                    board[r][c] = None
        return best
    else:
        best = 100
        opponent = _opponent(ai)
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = opponent
                    best = min(best, minimax(board, True, ai, depth + 1))
                    board[r][c] = None
        return best


def best_move(board: Board, ai: Player) -> tuple[int, int] | None:
    """Find the best move for the AI player."""
    best_score = -100
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] is None:
                board[r][c] = ai
                score = minimax(board, False, ai, 0)
                board[r][c] = None
                if score > best_score:
                    best_score = score
                    move = (r, c)
    return move
