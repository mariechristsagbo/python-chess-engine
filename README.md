# Chess Engine

Small chess engine in Python built on top of `python-chess`.

This version uses `python-chess` for:

- board representation
- FEN parsing
- legal move generation
- check and game-over detection

That lets you focus on the engine parts that still teach a lot:

- evaluation
- search
- move ordering
- engine orchestration
- CLI design

## Project Layout

```text
python-chess-engine/
├── src/
│   └── chess_engine/
│       ├── __init__.py
│       ├── board.py
│       ├── move_generator.py
│       ├── evaluation.py
│       ├── search.py
│       ├── engine.py
│       └── main.py
├── tests/
│   └── test_board.py
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

## What The Code Does

- `board.py`: wraps `python-chess` and exposes your project API
- `move_generator.py`: returns legal and pseudo-legal moves from the wrapped board
- `evaluation.py`: scores a position from White's point of view
- `search.py`: alpha-beta search with a simple move-ordering heuristic
- `engine.py`: small high-level engine wrapper
- `main.py`: terminal commands for `bestmove` and `play`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
chess-engine bestmove --depth 2
```

## Example

```bash
chess-engine bestmove --depth 2 --fen "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 2 3"
```

## Next Improvements

1. Add piece-square tables to `evaluation.py`.
2. Add quiescence search to reduce tactical blunders.
3. Add iterative deepening and a time limit.
4. Add a transposition table.
5. Add a UCI interface so you can use the engine in a GUI.

