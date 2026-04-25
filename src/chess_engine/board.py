"""Board and move wrappers around python-chess."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import chess

FILES = "abcdefgh"
RANKS = "12345678"
BOARD_SIZE = 8
STARTING_FEN = chess.STARTING_FEN


def opposite(color: str) -> str:
    if color == "w":
        return "b"
    if color == "b":
        return "w"
    raise ValueError(f"Invalid color: {color!r}")


def color_of(piece: str) -> Optional[str]:
    if piece == ".":
        return None
    if len(piece) != 1 or piece.lower() not in {"p", "n", "b", "r", "q", "k"}:
        raise ValueError(f"Invalid piece symbol: {piece!r}")
    return "w" if piece.isupper() else "b"


def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def square_to_coords(square: str) -> Tuple[int, int]:
    if len(square) != 2 or square[0] not in FILES or square[1] not in RANKS:
        raise ValueError(f"Invalid square: {square!r}")
    return BOARD_SIZE - int(square[1]), FILES.index(square[0])


def coords_to_square(row: int, col: int) -> str:
    if not in_bounds(row, col):
        raise ValueError(f"Invalid board coordinates: {(row, col)!r}")
    return f"{FILES[col]}{BOARD_SIZE - row}"


def _square_index(row: int, col: int) -> chess.Square:
    return chess.parse_square(coords_to_square(row, col))


def _turn_from_color(color: str) -> chess.Color:
    if color == "w":
        return chess.WHITE
    if color == "b":
        return chess.BLACK
    raise ValueError(f"Invalid color: {color!r}")


@dataclass(frozen=True)
class Move:
    uci_text: str

    @classmethod
    def from_uci(cls, uci: str) -> "Move":
        normalized = uci.strip().lower()
        try:
            chess.Move.from_uci(normalized)
        except ValueError as error:
            raise ValueError(f"Invalid UCI move: {uci!r}") from error
        return cls(normalized)

    @classmethod
    def from_chess(cls, move: chess.Move) -> "Move":
        return cls(move.uci())

    def to_chess(self) -> chess.Move:
        return chess.Move.from_uci(self.uci_text)

    def to_uci(self) -> str:
        return self.uci_text

    def __str__(self) -> str:
        return self.uci_text


@dataclass
class Board:
    position: chess.Board = field(default_factory=chess.Board)

    @classmethod
    def starting_position(cls) -> "Board":
        return cls(chess.Board())

    @classmethod
    def from_fen(cls, fen: str) -> "Board":
        try:
            return cls(chess.Board(fen))
        except ValueError as error:
            raise ValueError(f"Invalid FEN: {fen!r}") from error

    @property
    def side_to_move(self) -> str:
        return "w" if self.position.turn == chess.WHITE else "b"

    @property
    def squares(self) -> List[List[str]]:
        return [[self.piece_at(row, col) for col in range(BOARD_SIZE)] for row in range(BOARD_SIZE)]

    def copy(self) -> "Board":
        return Board(self.position.copy(stack=True))

    def piece_at(self, row: int, col: int) -> str:
        piece = self.position.piece_at(_square_index(row, col))
        return piece.symbol() if piece else "."

    def set_piece(self, row: int, col: int, piece: str) -> None:
        square = _square_index(row, col)
        if piece == ".":
            self.position.remove_piece_at(square)
            return

        try:
            piece_obj = chess.Piece.from_symbol(piece)
        except ValueError as error:
            raise ValueError(f"Invalid piece symbol: {piece!r}") from error
        self.position.set_piece_at(square, piece_obj)

    def make_move(self, move: Move) -> None:
        chess_move = move.to_chess()
        if chess_move not in self.position.legal_moves:
            raise ValueError(f"Illegal move: {move.to_uci()}")
        self.position.push(chess_move)

    def legal_moves(self) -> List[Move]:
        from .move_generator import generate_legal_moves

        return generate_legal_moves(self)

    def is_in_check(self, color: Optional[str] = None) -> bool:
        from .move_generator import is_in_check

        return is_in_check(self, color or self.side_to_move)

    def fen(self) -> str:
        return self.position.fen()

    def to_ascii(self) -> str:
        return str(self.position)

    def __str__(self) -> str:
        return self.to_ascii()

