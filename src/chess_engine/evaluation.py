"""Position evaluation.

Start simple:
- material count

Then add:
- piece-square tables
- mobility
- king safety
- pawn structure
"""

from __future__ import annotations

from .board import Board


def evaluate(board: Board) -> int:
    raise NotImplementedError("TODO: return a score from White's point of view.")

