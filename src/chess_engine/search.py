"""Alpha-beta search built on top of the board wrapper."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .board import Board, Move
from .evaluation import PIECE_VALUES, evaluate
from .move_generator import generate_legal_moves

MATE_SCORE = 100_000


def find_best_move(board: Board, depth: int) -> Tuple[Optional[Move], int]:
    search_depth = max(1, depth)
    legal_moves = order_moves(board, generate_legal_moves(board))
    if not legal_moves:
        return None, _terminal_score(board, search_depth)

    alpha = -math.inf
    beta = math.inf
    best_move = None
    best_score = -math.inf

    for move in legal_moves:
        candidate = board.copy()
        candidate.make_move(move)
        score = -negamax(candidate, search_depth - 1, -beta, -alpha)
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)

    return best_move, int(best_score)


def negamax(board: Board, depth: int, alpha: float, beta: float) -> int:
    if depth <= 0 or board.position.is_game_over(claim_draw=True):
        return _leaf_score(board, depth)

    moves = order_moves(board, generate_legal_moves(board))
    if not moves:
        return _terminal_score(board, depth)

    best_score = -math.inf
    for move in moves:
        candidate = board.copy()
        candidate.make_move(move)
        score = -negamax(candidate, depth - 1, -beta, -alpha)
        best_score = max(best_score, score)
        alpha = max(alpha, score)
        if alpha >= beta:
            break

    return int(best_score)


def order_moves(board: Board, moves: List[Move]) -> List[Move]:
    return sorted(moves, key=lambda move: _move_score(board, move), reverse=True)


def _leaf_score(board: Board, depth: int) -> int:
    if board.position.is_game_over(claim_draw=True):
        return _terminal_score(board, depth)

    raw_score = evaluate(board)
    return raw_score if board.side_to_move == "w" else -raw_score


def _terminal_score(board: Board, depth: int) -> int:
    if board.position.is_checkmate():
        return -MATE_SCORE - depth
    return 0


def _move_score(board: Board, move: Move) -> int:
    chess_move = move.to_chess()
    score = 0

    if board.position.is_capture(chess_move):
        victim = board.position.piece_at(chess_move.to_square)
        attacker = board.position.piece_at(chess_move.from_square)
        if victim is not None and attacker is not None:
            score += (10 * PIECE_VALUES[victim.piece_type]) - PIECE_VALUES[attacker.piece_type]
        else:
            score += 1000

    if chess_move.promotion is not None:
        score += PIECE_VALUES[chess_move.promotion]

    if board.position.gives_check(chess_move):
        score += 50

    return score

