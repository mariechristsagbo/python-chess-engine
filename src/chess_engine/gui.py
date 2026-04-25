"""Tkinter GUI for testing the chess engine interactively."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Dict, List, Optional, Sequence, Set

from .board import BOARD_SIZE, Board, Move, color_of, coords_to_square
from .engine import ChessEngine

LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#b58863"
SELECTED_SQUARE = "#f7ec74"
TARGET_SQUARE = "#a7d08c"
LAST_MOVE_SQUARE = "#e6c16a"

PIECE_UNICODE = {
    ".": "",
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",
}


class ChessGUI:
    def __init__(self, depth: int, fen: str, human_color: str) -> None:
        self.root = tk.Tk()
        self.root.title("Chess Engine")
        self.root.resizable(False, False)

        self.engine = ChessEngine(depth=depth)
        self.board = Board.from_fen(fen)
        self.human_color = human_color
        self.flipped = human_color == "b"

        self.selected_square: Optional[str] = None
        self.legal_targets: Set[str] = set()
        self.moves_by_target: Dict[str, List[Move]] = {}
        self.last_move_squares: Set[str] = set()

        self.status_var = tk.StringVar()
        self.fen_var = tk.StringVar(value=self.board.fen())
        self.buttons: List[List[tk.Button]] = []

        self._build_layout()
        self._refresh_board()
        self._set_status("Ready.")
        self.root.after(100, self._maybe_engine_move)

    def run(self) -> int:
        self.root.mainloop()
        return 0

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, padx=12, pady=12)
        container.grid(row=0, column=0, sticky="nsew")

        controls = tk.Frame(container)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(controls, text="FEN").grid(row=0, column=0, sticky="w")
        fen_entry = tk.Entry(controls, width=78, textvariable=self.fen_var)
        fen_entry.grid(row=0, column=1, columnspan=4, sticky="ew", padx=(6, 8))

        tk.Button(controls, text="Load FEN", command=self._load_fen).grid(row=0, column=5, padx=2)
        tk.Button(controls, text="Reset", command=self._reset_board).grid(row=0, column=6, padx=2)
        tk.Button(controls, text="Flip", command=self._flip_board).grid(row=0, column=7, padx=2)
        tk.Button(controls, text="Engine Move", command=self._engine_move).grid(row=0, column=8, padx=(8, 0))

        board_frame = tk.Frame(container, bd=2, relief=tk.FLAT)
        board_frame.grid(row=1, column=0)

        for display_row in range(BOARD_SIZE):
            button_row: List[tk.Button] = []
            for display_col in range(BOARD_SIZE):
                button = tk.Button(
                    board_frame,
                    width=3,
                    height=1,
                    font=("Arial Unicode MS", 28),
                    relief=tk.FLAT,
                    command=lambda row=display_row, col=display_col: self._handle_square_click(row, col),
                )
                button.grid(row=display_row, column=display_col, ipadx=10, ipady=8)
                button_row.append(button)
            self.buttons.append(button_row)

        self.status_label = tk.Label(
            container,
            textvariable=self.status_var,
            anchor="w",
            justify="left",
            width=72,
            pady=10,
        )
        self.status_label.grid(row=2, column=0, sticky="ew")

    def _display_to_board_coords(self, display_row: int, display_col: int) -> tuple[int, int]:
        if self.flipped:
            return BOARD_SIZE - 1 - display_row, BOARD_SIZE - 1 - display_col
        return display_row, display_col

    def _handle_square_click(self, display_row: int, display_col: int) -> None:
        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Game over.")
            return

        if not self._human_controls_side_to_move():
            self._set_status("It is the engine's turn.")
            return

        row, col = self._display_to_board_coords(display_row, display_col)
        square = coords_to_square(row, col)
        piece = self.board.piece_at(row, col)

        if self.selected_square is None:
            self._select_square(square, piece)
            return

        if square == self.selected_square:
            self._clear_selection()
            self._set_status("Selection cleared.")
            return

        if square in self.legal_targets:
            self._play_human_move(square)
            return

        self._select_square(square, piece)

    def _select_square(self, square: str, piece: str) -> None:
        if piece == "." or color_of(piece) != self.board.side_to_move:
            self._clear_selection()
            self._set_status("Select a piece for the side to move.")
            return

        legal_from_square = [move for move in self.board.legal_moves() if move.to_uci()[:2] == square]
        if not legal_from_square:
            self._clear_selection()
            self._set_status("That piece has no legal moves.")
            return

        self.selected_square = square
        self.moves_by_target = {}
        for move in legal_from_square:
            target = move.to_uci()[2:4]
            self.moves_by_target.setdefault(target, []).append(move)
        self.legal_targets = set(self.moves_by_target)
        self._refresh_board()
        self._set_status(f"Selected {square}. Choose a destination square.")

    def _play_human_move(self, target_square: str) -> None:
        candidate_moves = self.moves_by_target[target_square]
        move = candidate_moves[0]

        if len(candidate_moves) > 1:
            move = self._choose_promotion(candidate_moves)
            if move is None:
                self._set_status("Promotion cancelled.")
                return

        self.board.make_move(move)
        self._record_last_move(move)
        self._clear_selection()
        self._refresh_board()

        outcome = self._outcome_text()
        if outcome:
            self._set_status(outcome)
            messagebox.showinfo("Game Over", outcome)
            return

        self._set_status(f"You played {move.to_uci()}.")
        self.root.after(100, self._maybe_engine_move)

    def _choose_promotion(self, candidate_moves: Sequence[Move]) -> Optional[Move]:
        response = simpledialog.askstring(
            "Promotion",
            "Promote to one of: q, r, b, n",
            initialvalue="q",
            parent=self.root,
        )
        if response is None:
            return None

        promotion = response.strip().lower()
        for move in candidate_moves:
            if move.to_uci().endswith(promotion):
                return move

        messagebox.showerror("Promotion", f"Invalid promotion piece: {response!r}")
        return None

    def _human_controls_side_to_move(self) -> bool:
        return self.human_color == "both" or self.board.side_to_move == self.human_color

    def _maybe_engine_move(self) -> None:
        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Game over.")
            return
        if self.human_color == "both" or self.board.side_to_move == self.human_color:
            return
        self._engine_move()

    def _engine_move(self) -> None:
        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Game over.")
            return

        self._clear_selection()
        self._set_status("Engine thinking...")
        self.root.update_idletasks()

        move, score = self.engine.analyze(self.board)
        if move is None:
            outcome = self._outcome_text() or "No legal moves."
            self._set_status(outcome)
            messagebox.showinfo("Game Over", outcome)
            return

        self.board.make_move(move)
        self._record_last_move(move)
        self._refresh_board()

        outcome = self._outcome_text()
        if outcome:
            self._set_status(outcome)
            messagebox.showinfo("Game Over", outcome)
            return

        self._set_status(f"Engine played {move.to_uci()} with score {score}.")

    def _record_last_move(self, move: Move) -> None:
        uci = move.to_uci()
        self.last_move_squares = {uci[:2], uci[2:4]}
        self.fen_var.set(self.board.fen())

    def _clear_selection(self) -> None:
        self.selected_square = None
        self.legal_targets = set()
        self.moves_by_target = {}
        self._refresh_board()

    def _load_fen(self) -> None:
        try:
            self.board = Board.from_fen(self.fen_var.get().strip())
        except ValueError as error:
            messagebox.showerror("Invalid FEN", str(error))
            return

        self.last_move_squares = set()
        self._clear_selection()
        self._refresh_board()
        self._set_status("Position loaded.")
        self.root.after(100, self._maybe_engine_move)

    def _reset_board(self) -> None:
        self.board = Board.starting_position()
        self.fen_var.set(self.board.fen())
        self.last_move_squares = set()
        self._clear_selection()
        self._refresh_board()
        self._set_status("Board reset to the starting position.")
        self.root.after(100, self._maybe_engine_move)

    def _flip_board(self) -> None:
        self.flipped = not self.flipped
        self._refresh_board()
        self._set_status("Board flipped.")

    def _refresh_board(self) -> None:
        for display_row in range(BOARD_SIZE):
            for display_col in range(BOARD_SIZE):
                row, col = self._display_to_board_coords(display_row, display_col)
                square = coords_to_square(row, col)
                piece = self.board.piece_at(row, col)

                button = self.buttons[display_row][display_col]
                button.configure(
                    text=PIECE_UNICODE[piece],
                    fg="#111111",
                    bg=self._square_color(row, col, square),
                    activebackground=self._square_color(row, col, square),
                    relief=tk.SUNKEN if square == self.selected_square else tk.FLAT,
                )

    def _square_color(self, row: int, col: int, square: str) -> str:
        if square == self.selected_square:
            return SELECTED_SQUARE
        if square in self.legal_targets:
            return TARGET_SQUARE
        if square in self.last_move_squares:
            return LAST_MOVE_SQUARE
        return LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _outcome_text(self) -> Optional[str]:
        outcome = self.board.position.outcome(claim_draw=True)
        if outcome is None:
            return None
        if outcome.winner is None:
            return f"Game over: draw by {outcome.termination.name.lower().replace('_', ' ')}."

        winner = "White" if outcome.winner else "Black"
        return f"Game over: {winner} wins by {outcome.termination.name.lower().replace('_', ' ')}."


def run_gui(depth: int, fen: str, human_color: str) -> int:
    app = ChessGUI(depth=depth, fen=fen, human_color=human_color)
    return app.run()
