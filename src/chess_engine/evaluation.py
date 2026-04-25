"""Position evaluation."""

from __future__ import annotations

import chess

from .board import Board

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
}


def evaluate(board: Board) -> int:
    """Return a score from White's point of view."""
    score = 0

    for square, piece in board.position.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        value += _piece_square_bonus(piece, square)
        score += value if piece.color == chess.WHITE else -value

    return score


def _piece_square_bonus(piece: chess.Piece, square: chess.Square) -> int:
    table = PIECE_SQUARE_TABLES.get(piece.piece_type)
    if table is None:
        return 0

    rank = chess.square_rank(square)
    file_index = chess.square_file(square)
    row = 7 - rank

    if piece.color == chess.WHITE:
        return table[row][file_index]
    return table[7 - row][file_index]
