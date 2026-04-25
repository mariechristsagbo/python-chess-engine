"""High-level engine wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .board import Board, Move
from .search import find_best_move


@dataclass
class ChessEngine:
    depth: int = 2

    def analyze(self, board: Board) -> Tuple[Optional[Move], int]:
        return find_best_move(board, self.depth)

    def choose_move(self, board: Board) -> Optional[Move]:
        move, _ = self.analyze(board)
        return move

