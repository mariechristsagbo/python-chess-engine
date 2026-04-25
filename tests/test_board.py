from chess_engine.board import Board, Move
from chess_engine.engine import ChessEngine


def test_starting_position_contains_expected_pieces() -> None:
    board = Board.starting_position()

    assert board.piece_at(0, 4) == "k"
    assert board.piece_at(7, 4) == "K"
    assert board.piece_at(1, 0) == "p"
    assert board.piece_at(6, 7) == "P"


def test_starting_position_has_twenty_legal_moves() -> None:
    board = Board.starting_position()
    legal_moves = {move.to_uci() for move in board.legal_moves()}

    assert len(legal_moves) == 20
    assert {"e2e4", "d2d4", "g1f3", "b1c3"}.issubset(legal_moves)


def test_make_move_updates_board_and_side_to_move() -> None:
    board = Board.starting_position()
    board.make_move(Move.from_uci("e2e4"))

    assert board.piece_at(6, 4) == "."
    assert board.piece_at(4, 4) == "P"
    assert board.side_to_move == "b"


def test_simple_check_detection_from_fen() -> None:
    board = Board.from_fen("4k3/8/8/8/8/8/4R3/4K3 b - - 0 1")

    assert board.is_in_check("b") is True
    assert board.is_in_check("w") is False


def test_engine_returns_a_legal_move() -> None:
    board = Board.starting_position()
    engine = ChessEngine(depth=1)

    move = engine.choose_move(board)

    assert move is not None
    assert move.to_uci() in {candidate.to_uci() for candidate in board.legal_moves()}
