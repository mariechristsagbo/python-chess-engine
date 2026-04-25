"""Move-generation helpers backed by python-chess."""

from __future__ import annotations

from typing import List

from .board import Board, Move, _square_index, _turn_from_color


def generate_legal_moves(board: Board) -> List[Move]:
    return [Move.from_chess(move) for move in board.position.legal_moves]


def generate_pseudo_legal_moves(board: Board) -> List[Move]:
    return [Move.from_chess(move) for move in board.position.pseudo_legal_moves]


def is_in_check(board: Board, color: str) -> bool:
    turn = _turn_from_color(color)
    king_square = board.position.king(turn)
    if king_square is None:
        raise ValueError(f"King not found for color {color!r}")
    return board.position.is_attacked_by(not turn, king_square)


def is_square_attacked(board: Board, row: int, col: int, by_color: str) -> bool:
    return board.position.is_attacked_by(_turn_from_color(by_color), _square_index(row, col))

