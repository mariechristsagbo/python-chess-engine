"""Tkinter GUI for testing the chess engine interactively."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Dict, List, Optional, Sequence, Set

import chess

from .board import BOARD_SIZE, Board, Move, STARTING_FEN, color_of, coords_to_square
from .engine import ChessEngine

APP_BG = "#262421"
PANEL_BG = "#312e2b"
PANEL_BORDER = "#4d493f"
TEXT_PRIMARY = "#f3f1ec"
TEXT_MUTED = "#b9b4aa"
BUTTON_BG = "#6a9b41"
BUTTON_BG_ALT = "#4a4740"
BUTTON_FG = "#ffffff"
ENTRY_BG = "#1f1d1a"
ENTRY_FG = "#f1eee8"

LIGHT_SQUARE = "#eeeed2"
DARK_SQUARE = "#769656"
LAST_MOVE_LIGHT = "#f5f682"
LAST_MOVE_DARK = "#b9ca43"
SELECTED_LIGHT = "#f7f26b"
SELECTED_DARK = "#c2cf4b"
MOVE_DOT = "#435d30"
MOVE_RING = "#2e2d29"
BOARD_OUTLINE = "#1d1b18"

SQUARE_SIZE = 84
BOARD_PIXELS = SQUARE_SIZE * BOARD_SIZE

PIECE_FONT = ("Arial Unicode MS", 46)
COORD_FONT = ("Helvetica", 11, "bold")
TITLE_FONT = ("Helvetica", 18, "bold")
SUBTITLE_FONT = ("Helvetica", 11)
STATUS_FONT = ("Helvetica", 12)
LABEL_FONT = ("Helvetica", 11, "bold")
BUTTON_FONT = ("Helvetica", 11, "bold")
MOVE_FONT = ("Menlo", 11)

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
        self.root.configure(bg=APP_BG)
        self.root.resizable(False, False)

        self.engine = ChessEngine(depth=depth)
        self.board = Board.from_fen(fen)
        self.initial_fen = self.board.fen()
        self.human_color = human_color
        self.flipped = human_color == "b"
        self.depth = depth

        self.selected_square: Optional[str] = None
        self.legal_targets: Set[str] = set()
        self.moves_by_target: Dict[str, List[Move]] = {}
        self.last_move_squares: Set[str] = set()

        self.status_var = tk.StringVar()
        self.turn_var = tk.StringVar()
        self.mode_var = tk.StringVar()
        self.fen_var = tk.StringVar(value=self.board.fen())

        self.board_canvas: Optional[tk.Canvas] = None
        self.move_listbox: Optional[tk.Listbox] = None

        self._build_layout()
        self._refresh_board()
        self._set_status("Plateau prêt.")
        self.root.after(100, self._maybe_engine_move)

    def run(self) -> int:
        self.root.mainloop()
        return 0

    def _build_layout(self) -> None:
        container = tk.Frame(self.root, bg=APP_BG, padx=18, pady=18)
        container.grid(row=0, column=0)

        board_shell = tk.Frame(container, bg=PANEL_BORDER, padx=10, pady=10)
        board_shell.grid(row=0, column=0, sticky="n")

        self.board_canvas = tk.Canvas(
            board_shell,
            width=BOARD_PIXELS,
            height=BOARD_PIXELS,
            bg=BOARD_OUTLINE,
            highlightthickness=0,
            bd=0,
        )
        self.board_canvas.grid(row=0, column=0)
        self.board_canvas.bind("<Button-1>", self._handle_canvas_click)

        sidebar = tk.Frame(container, bg=PANEL_BG, padx=18, pady=18, width=300)
        sidebar.grid(row=0, column=1, sticky="ns", padx=(18, 0))
        sidebar.grid_propagate(False)

        header = tk.Frame(sidebar, bg=PANEL_BG)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="Chess Engine", font=TITLE_FONT, fg=TEXT_PRIMARY, bg=PANEL_BG).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(
            header,
            text="Interface de test style chess.com",
            font=SUBTITLE_FONT,
            fg=TEXT_MUTED,
            bg=PANEL_BG,
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        info_box = tk.Frame(sidebar, bg=ENTRY_BG, padx=12, pady=10)
        info_box.grid(row=1, column=0, sticky="ew")
        tk.Label(info_box, textvariable=self.turn_var, font=LABEL_FONT, fg=TEXT_PRIMARY, bg=ENTRY_BG).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(info_box, textvariable=self.mode_var, font=SUBTITLE_FONT, fg=TEXT_MUTED, bg=ENTRY_BG).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        tk.Label(sidebar, text="FEN", font=LABEL_FONT, fg=TEXT_PRIMARY, bg=PANEL_BG).grid(
            row=2, column=0, sticky="w", pady=(16, 6)
        )
        fen_entry = tk.Entry(
            sidebar,
            textvariable=self.fen_var,
            width=36,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            insertbackground=ENTRY_FG,
            relief=tk.FLAT,
            font=("Menlo", 10),
        )
        fen_entry.grid(row=3, column=0, sticky="ew")

        actions = tk.Frame(sidebar, bg=PANEL_BG)
        actions.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        self._build_button(actions, "Load FEN", self._load_fen).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._build_button(actions, "Reset", self._reset_board, alt=True).grid(row=0, column=1, sticky="ew")
        self._build_button(actions, "Flip", self._flip_board, alt=True).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(8, 0))
        self._build_button(actions, "Engine Move", self._engine_move).grid(row=1, column=1, sticky="ew", pady=(8, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Label(sidebar, text="Historique", font=LABEL_FONT, fg=TEXT_PRIMARY, bg=PANEL_BG).grid(
            row=5, column=0, sticky="w", pady=(18, 6)
        )
        history_frame = tk.Frame(sidebar, bg=ENTRY_BG, padx=6, pady=6)
        history_frame.grid(row=6, column=0, sticky="nsew")
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        self.move_listbox = tk.Listbox(
            history_frame,
            bg=ENTRY_BG,
            fg=TEXT_PRIMARY,
            selectbackground=ENTRY_BG,
            selectforeground=TEXT_PRIMARY,
            highlightthickness=0,
            activestyle="none",
            relief=tk.FLAT,
            font=MOVE_FONT,
            height=15,
        )
        self.move_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(history_frame, command=self.move_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.move_listbox.configure(yscrollcommand=scrollbar.set)

        tk.Label(sidebar, text="Statut", font=LABEL_FONT, fg=TEXT_PRIMARY, bg=PANEL_BG).grid(
            row=7, column=0, sticky="w", pady=(18, 6)
        )
        tk.Label(
            sidebar,
            textvariable=self.status_var,
            font=STATUS_FONT,
            fg=TEXT_PRIMARY,
            bg=ENTRY_BG,
            anchor="nw",
            justify="left",
            wraplength=260,
            padx=12,
            pady=12,
            height=5,
        ).grid(row=8, column=0, sticky="ew")

        sidebar.grid_rowconfigure(6, weight=1)

    def _build_button(self, parent: tk.Widget, text: str, command, alt: bool = False) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=BUTTON_FONT,
            bg=BUTTON_BG_ALT if alt else BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_BG,
            activeforeground=BUTTON_FG,
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
        )

    def _display_to_board_coords(self, display_row: int, display_col: int) -> tuple[int, int]:
        if self.flipped:
            return BOARD_SIZE - 1 - display_row, BOARD_SIZE - 1 - display_col
        return display_row, display_col

    def _handle_canvas_click(self, event: tk.Event) -> None:
        display_row = event.y // SQUARE_SIZE
        display_col = event.x // SQUARE_SIZE
        if not (0 <= display_row < BOARD_SIZE and 0 <= display_col < BOARD_SIZE):
            return

        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Partie terminée.")
            return

        if not self._human_controls_side_to_move():
            self._set_status("C'est le tour du moteur.")
            return

        row, col = self._display_to_board_coords(display_row, display_col)
        square = coords_to_square(row, col)
        piece = self.board.piece_at(row, col)

        if self.selected_square is None:
            self._select_square(square, piece)
            return

        if square == self.selected_square:
            self._clear_selection()
            self._set_status("Sélection annulée.")
            return

        if square in self.legal_targets:
            self._play_human_move(square)
            return

        self._select_square(square, piece)

    def _select_square(self, square: str, piece: str) -> None:
        if piece == "." or color_of(piece) != self.board.side_to_move:
            self._clear_selection()
            self._set_status("Sélectionne une pièce du camp qui doit jouer.")
            return

        legal_from_square = [move for move in self.board.legal_moves() if move.to_uci()[:2] == square]
        if not legal_from_square:
            self._clear_selection()
            self._set_status("Cette pièce n'a aucun coup légal.")
            return

        self.selected_square = square
        self.moves_by_target = {}
        for move in legal_from_square:
            target = move.to_uci()[2:4]
            self.moves_by_target.setdefault(target, []).append(move)
        self.legal_targets = set(self.moves_by_target)
        self._refresh_board()
        self._set_status(f"{square} sélectionnée. Choisis une case d'arrivée.")

    def _play_human_move(self, target_square: str) -> None:
        candidate_moves = self.moves_by_target[target_square]
        move = candidate_moves[0]

        if len(candidate_moves) > 1:
            move = self._choose_promotion(candidate_moves)
            if move is None:
                self._set_status("Promotion annulée.")
                return

        self.board.make_move(move)
        self._record_last_move(move)
        self._clear_selection()

        outcome = self._outcome_text()
        if outcome:
            self._set_status(outcome)
            messagebox.showinfo("Partie terminée", outcome)
            return

        self._set_status(f"Tu as joué {move.to_uci()}.")
        self.root.after(100, self._maybe_engine_move)

    def _choose_promotion(self, candidate_moves: Sequence[Move]) -> Optional[Move]:
        response = simpledialog.askstring(
            "Promotion",
            "Choisis une promotion: q, r, b, n",
            initialvalue="q",
            parent=self.root,
        )
        if response is None:
            return None

        promotion = response.strip().lower()
        for move in candidate_moves:
            if move.to_uci().endswith(promotion):
                return move

        messagebox.showerror("Promotion", f"Pièce de promotion invalide: {response!r}")
        return None

    def _human_controls_side_to_move(self) -> bool:
        return self.human_color == "both" or self.board.side_to_move == self.human_color

    def _maybe_engine_move(self) -> None:
        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Partie terminée.")
            return
        if self.human_color == "both" or self.board.side_to_move == self.human_color:
            return
        self._engine_move()

    def _engine_move(self) -> None:
        if self.board.position.is_game_over(claim_draw=True):
            self._set_status(self._outcome_text() or "Partie terminée.")
            return

        self._clear_selection()
        self._set_status("Le moteur réfléchit...")
        self.root.update_idletasks()

        move, score = self.engine.analyze(self.board)
        if move is None:
            outcome = self._outcome_text() or "Aucun coup légal."
            self._set_status(outcome)
            messagebox.showinfo("Partie terminée", outcome)
            return

        self.board.make_move(move)
        self._record_last_move(move)

        outcome = self._outcome_text()
        if outcome:
            self._set_status(outcome)
            messagebox.showinfo("Partie terminée", outcome)
            return

        self._set_status(f"Le moteur a joué {move.to_uci()} avec un score de {score}.")

    def _record_last_move(self, move: Move) -> None:
        uci = move.to_uci()
        self.last_move_squares = {uci[:2], uci[2:4]}
        self.fen_var.set(self.board.fen())
        self._refresh_board()

    def _clear_selection(self) -> None:
        self.selected_square = None
        self.legal_targets = set()
        self.moves_by_target = {}
        self._refresh_board()

    def _load_fen(self) -> None:
        try:
            self.board = Board.from_fen(self.fen_var.get().strip())
        except ValueError as error:
            messagebox.showerror("FEN invalide", str(error))
            return

        self.initial_fen = self.board.fen()
        self.last_move_squares = set()
        self._clear_selection()
        self._set_status("Position chargée.")
        self.root.after(100, self._maybe_engine_move)

    def _reset_board(self) -> None:
        self.board = Board.starting_position()
        self.initial_fen = STARTING_FEN
        self.fen_var.set(self.board.fen())
        self.last_move_squares = set()
        self._clear_selection()
        self._set_status("Plateau réinitialisé.")
        self.root.after(100, self._maybe_engine_move)

    def _flip_board(self) -> None:
        self.flipped = not self.flipped
        self._refresh_board()
        self._set_status("Orientation inversée.")

    def _refresh_board(self) -> None:
        if self.board_canvas is None:
            return

        self.board_canvas.delete("all")

        for display_row in range(BOARD_SIZE):
            for display_col in range(BOARD_SIZE):
                row, col = self._display_to_board_coords(display_row, display_col)
                square = coords_to_square(row, col)
                piece = self.board.piece_at(row, col)
                x1 = display_col * SQUARE_SIZE
                y1 = display_row * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                base_color = self._square_color(row, col, square)
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=base_color, outline=base_color)

                if square in self.legal_targets:
                    self._draw_move_hint(display_row, display_col, piece != ".")

                self._draw_coordinates(display_row, display_col, square, base_color)
                self._draw_piece(display_row, display_col, piece)

        self._refresh_sidebar()

    def _draw_move_hint(self, display_row: int, display_col: int, occupied: bool) -> None:
        if self.board_canvas is None:
            return

        x1 = display_col * SQUARE_SIZE
        y1 = display_row * SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE
        y2 = y1 + SQUARE_SIZE
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        if occupied:
            margin = 8
            self.board_canvas.create_oval(
                x1 + margin,
                y1 + margin,
                x2 - margin,
                y2 - margin,
                outline=MOVE_RING,
                width=4,
            )
            return

        radius = 12
        self.board_canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=MOVE_DOT,
            outline=MOVE_DOT,
        )

    def _draw_coordinates(self, display_row: int, display_col: int, square: str, base_color: str) -> None:
        if self.board_canvas is None:
            return

        coord_color = "#5b6f43" if base_color in {LIGHT_SQUARE, LAST_MOVE_LIGHT, SELECTED_LIGHT} else "#f3f3eb"
        x1 = display_col * SQUARE_SIZE
        y1 = display_row * SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE
        y2 = y1 + SQUARE_SIZE

        if display_col == 0:
            self.board_canvas.create_text(
                x1 + 9,
                y1 + 12,
                text=square[1],
                fill=coord_color,
                font=COORD_FONT,
                anchor="nw",
            )

        if display_row == BOARD_SIZE - 1:
            self.board_canvas.create_text(
                x2 - 10,
                y2 - 8,
                text=square[0],
                fill=coord_color,
                font=COORD_FONT,
                anchor="se",
            )

    def _draw_piece(self, display_row: int, display_col: int, piece: str) -> None:
        if self.board_canvas is None or piece == ".":
            return

        x1 = display_col * SQUARE_SIZE
        y1 = display_row * SQUARE_SIZE
        center_x = x1 + (SQUARE_SIZE / 2)
        center_y = y1 + (SQUARE_SIZE / 2) + 2

        shadow_color = "#1b1a18"
        piece_color = "#f7f7f5" if piece.isupper() else "#1e1e1c"

        self.board_canvas.create_text(
            center_x + 2,
            center_y + 3,
            text=PIECE_UNICODE[piece],
            font=PIECE_FONT,
            fill=shadow_color,
        )
        self.board_canvas.create_text(
            center_x,
            center_y,
            text=PIECE_UNICODE[piece],
            font=PIECE_FONT,
            fill=piece_color,
        )

    def _refresh_sidebar(self) -> None:
        side_text = "Blanc" if self.board.side_to_move == "w" else "Noir"
        if self.human_color == "both":
            mode_text = f"Mode analyse libre | profondeur {self.depth}"
        else:
            player_side = "Blanc" if self.human_color == "w" else "Noir"
            mode_text = f"Tu joues {player_side} | profondeur {self.depth}"

        self.turn_var.set(f"Trait: {side_text}")
        self.mode_var.set(mode_text)
        self._refresh_move_history()

    def _refresh_move_history(self) -> None:
        if self.move_listbox is None:
            return

        self.move_listbox.delete(0, tk.END)
        for line in self._history_lines():
            self.move_listbox.insert(tk.END, line)
        if self.move_listbox.size() > 0:
            self.move_listbox.yview_moveto(1.0)

    def _history_lines(self) -> List[str]:
        replay = chess.Board(self.initial_fen)
        san_moves: List[str] = []

        for move in self.board.position.move_stack:
            san_moves.append(replay.san(move))
            replay.push(move)

        lines = []
        for index in range(0, len(san_moves), 2):
            move_number = (index // 2) + 1
            white_move = san_moves[index]
            black_move = san_moves[index + 1] if index + 1 < len(san_moves) else ""
            line = f"{move_number}. {white_move}"
            if black_move:
                line += f"   {black_move}"
            lines.append(line)

        if not lines:
            lines.append("Aucun coup joué.")

        return lines

    def _square_color(self, row: int, col: int, square: str) -> str:
        is_light = (row + col) % 2 == 0
        if square == self.selected_square:
            return SELECTED_LIGHT if is_light else SELECTED_DARK
        if square in self.last_move_squares:
            return LAST_MOVE_LIGHT if is_light else LAST_MOVE_DARK
        return LIGHT_SQUARE if is_light else DARK_SQUARE

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _outcome_text(self) -> Optional[str]:
        outcome = self.board.position.outcome(claim_draw=True)
        if outcome is None:
            return None
        if outcome.winner is None:
            return f"Partie terminée: nulle par {outcome.termination.name.lower().replace('_', ' ')}."

        winner = "Blanc" if outcome.winner else "Noir"
        return f"Partie terminée: {winner} gagne par {outcome.termination.name.lower().replace('_', ' ')}."


def run_gui(depth: int, fen: str, human_color: str) -> int:
    app = ChessGUI(depth=depth, fen=fen, human_color=human_color)
    return app.run()
