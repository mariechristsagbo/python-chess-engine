"""High-level engine wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .board import Board, Move


@dataclass
class ChessEngine:
    depth: int = 2

    def analyze(self, board: Board) -> Tuple[Optional[Move], int]:
        raise NotImplementedError("TODO: call your search function and return move plus score.")

    def choose_move(self, board: Board) -> Optional[Move]:
        raise NotImplementedError("TODO: return only the selected move.")

