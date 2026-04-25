"""Search algorithms for the chess engine.

Suggested order:
1. minimax
2. negamax
3. alpha-beta pruning
4. move ordering
5. iterative deepening
6. quiescence search
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .board import Board, Move

MATE_SCORE = 100_000


def find_best_move(board: Board, depth: int) -> Tuple[Optional[Move], int]:
    raise NotImplementedError("TODO: search the position and return the best move plus its score.")


def negamax(board: Board, depth: int, alpha: float, beta: float) -> int:
    raise NotImplementedError("TODO: implement alpha-beta search with a negamax interface.")


def order_moves(board: Board, moves: List[Move]) -> List[Move]:
    raise NotImplementedError("TODO: sort moves to improve alpha-beta pruning.")

