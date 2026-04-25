"""Command-line interface for the engine."""

from __future__ import annotations

import argparse
from typing import List, Optional

from .board import Board, Move, STARTING_FEN
from .engine import ChessEngine
from .gui import run_gui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chess engine built on python-chess")
    subparsers = parser.add_subparsers(dest="command")

    play_parser = subparsers.add_parser("play", help="Play against the engine in the terminal")
    play_parser.add_argument("--depth", type=int, default=2, help="Search depth")
    play_parser.add_argument("--fen", default=STARTING_FEN, help="Starting FEN")
    play_parser.add_argument("--human-color", choices=("w", "b", "both"), default="w", help="Your side")

    bestmove_parser = subparsers.add_parser("bestmove", help="Show the best move from a position")
    bestmove_parser.add_argument("--depth", type=int, default=2, help="Search depth")
    bestmove_parser.add_argument("--fen", default=STARTING_FEN, help="Position FEN")

    gui_parser = subparsers.add_parser("gui", help="Open a Tkinter board for interactive testing")
    gui_parser.add_argument("--depth", type=int, default=2, help="Search depth")
    gui_parser.add_argument("--fen", default=STARTING_FEN, help="Starting FEN")
    gui_parser.add_argument("--human-color", choices=("w", "b", "both"), default="w", help="Your side")

    parser.add_argument("--version", action="store_true", help="Show the installed package version")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print("chess-engine")
        return 0

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "play":
        return _play(depth=args.depth, fen=args.fen, human_color=args.human_color)
    if args.command == "bestmove":
        return _best_move(depth=args.depth, fen=args.fen)
    if args.command == "gui":
        return run_gui(depth=args.depth, fen=args.fen, human_color=args.human_color)

    parser.error(f"Unknown command: {args.command}")
    return 2


def _play(depth: int, fen: str, human_color: str) -> int:
    board = Board.from_fen(fen)
    engine = ChessEngine(depth=depth)

    while True:
        print(board)
        outcome = _outcome(board)
        if outcome:
            print(outcome)
            return 0

        if human_color == "both" or board.side_to_move == human_color:
            user_input = input("Your move (uci, moves, fen, quit): ").strip().lower()
            if user_input in {"quit", "exit"}:
                return 0
            if user_input == "moves":
                print(" ".join(move.to_uci() for move in board.legal_moves()))
                continue
            if user_input == "fen":
                print(board.fen())
                continue

            try:
                board.make_move(Move.from_uci(user_input))
            except ValueError as error:
                print(error)
            continue

        move, score = engine.analyze(board)
        if move is None:
            print(_outcome(board) or "No legal moves.")
            return 0

        print(f"Engine plays {move.to_uci()} (score {score})")
        board.make_move(move)


def _best_move(depth: int, fen: str) -> int:
    board = Board.from_fen(fen)
    engine = ChessEngine(depth=depth)
    move, score = engine.analyze(board)

    if move is None:
        print(_outcome(board) or "No legal moves.")
        return 0

    print(move.to_uci())
    print(f"score {score}")
    return 0


def _outcome(board: Board) -> Optional[str]:
    outcome = board.position.outcome(claim_draw=True)
    if outcome is None:
        return None
    if outcome.winner is None:
        return f"Game over: draw by {outcome.termination.name.lower().replace('_', ' ')}."

    winner = "White" if outcome.winner else "Black"
    return f"Game over: {winner} wins by {outcome.termination.name.lower().replace('_', ' ')}."


if __name__ == "__main__":
    raise SystemExit(main())
