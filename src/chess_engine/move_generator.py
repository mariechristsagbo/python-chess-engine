"""Move generation for the chess engine.

Suggested milestones:
1. generate pawn moves
2. generate knight moves
3. generate sliding-piece moves
4. generate king moves
5. filter pseudo-legal moves into legal moves
6. add special moves later: castling and en passant
"""

from __future__ import annotations

from typing import List

from .board import Board, Move


def generate_legal_moves(board: Board) -> List[Move]:
    raise NotImplementedError("TODO: generate legal moves for the side to move.")


def generate_pseudo_legal_moves(board: Board) -> List[Move]:
    raise NotImplementedError("TODO: generate moves without checking king safety first.")


def is_in_check(board: Board, color: str) -> bool:
    raise NotImplementedError("TODO: detect whether the given side's king is under attack.")


def is_square_attacked(board: Board, row: int, col: int, by_color: str) -> bool:
    raise NotImplementedError("TODO: detect whether a square is attacked by the given side.")

