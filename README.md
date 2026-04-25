# Chess Engine

Learning-oriented chess engine scaffold in Python.

The implementation has been intentionally removed so you can build it by hand.
The project keeps the module split and packaging setup, but the engine logic is now a set of TODO stubs.

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

## Build Order

1. `board.py`: `Move`, `Board`, FEN loading, `piece_at`, `make_move`
2. `move_generator.py`: pseudo-legal moves for each piece
3. legality filtering: reject moves that leave your king in check
4. `evaluation.py`: material score first, then positional ideas
5. `search.py`: minimax, then alpha-beta pruning
6. `engine.py`: connect board + search
7. `main.py`: simple CLI
8. `tests/test_board.py`: grow tests as features land

## First Milestones

- parse a FEN into an 8x8 board
- print the board in ASCII
- generate 20 legal moves from the starting position
- detect check in a simple rook or bishop position
- return a best move at depth 1

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
```

## Recommended Workflow

- write one small feature
- add or update one test
- run tests
- ask for review when something feels unclear or wrong

