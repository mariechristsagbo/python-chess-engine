"""Board representation for the chess engine.

Suggested order inside this file:
1. coordinate helpers
2. Move dataclass
3. Board dataclass
4. FEN loading
5. make_move and board display helpers
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

FILES = "abcdefgh"
RANKS = "12345678"
BOARD_SIZE = 8
STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"


def opposite(color: str) -> str:
    raise NotImplementedError("TODO: return 'b' for 'w' and 'w' for 'b'.")


def color_of(piece: str) -> Optional[str]:
    raise NotImplementedError("TODO: return 'w', 'b', or None for an empty square.")


def in_bounds(row: int, col: int) -> bool:
    raise NotImplementedError("TODO: check whether row and col are inside the 8x8 board.")


def square_to_coords(square: str) -> Tuple[int, int]:
    raise NotImplementedError("TODO: convert algebraic notation like 'e4' into row/col indices.")


def coords_to_square(row: int, col: int) -> str:
    raise NotImplementedError("TODO: convert row/col indices back into algebraic notation.")


@dataclass(frozen=True)
class Move:
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    promotion: Optional[str] = None

    @classmethod
    def from_uci(cls, uci: str) -> "Move":
        raise NotImplementedError("TODO: parse a UCI move such as 'e2e4' or 'e7e8q'.")

    def to_uci(self) -> str:
        raise NotImplementedError("TODO: serialize this move into UCI notation.")


@dataclass
class Board:
    squares: List[List[str]]
    side_to_move: str = "w"

    @classmethod
    def starting_position(cls) -> "Board":
        raise NotImplementedError("TODO: build the initial board from STARTING_FEN.")

    @classmethod
    def from_fen(cls, fen: str) -> "Board":
        raise NotImplementedError("TODO: parse the board and side-to-move fields from a FEN string.")

    def copy(self) -> "Board":
        raise NotImplementedError("TODO: return a deep copy of the board state.")

    def piece_at(self, row: int, col: int) -> str:
        raise NotImplementedError("TODO: return the piece on the requested square.")

    def set_piece(self, row: int, col: int, piece: str) -> None:
        raise NotImplementedError("TODO: place a piece on the requested square.")

    def make_move(self, move: Move) -> None:
        raise NotImplementedError("TODO: move a piece, handle captures, promotion, and switch side to move.")

    def legal_moves(self) -> List[Move]:
        from .move_generator import generate_legal_moves

        return generate_legal_moves(self)

    def is_in_check(self, color: Optional[str] = None) -> bool:
        from .move_generator import is_in_check

        return is_in_check(self, color or self.side_to_move)

    def to_ascii(self) -> str:
        raise NotImplementedError("TODO: return a human-readable ASCII board.")

    def __str__(self) -> str:
        return self.to_ascii()

