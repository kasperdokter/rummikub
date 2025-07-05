# Rummikub

A Rummikub game implementation with AI hints using constraint programming.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rummikub
```

2. Configure Poetry to create virtual environment locally:
```bash
poetry config virtualenvs.in-project true
```

3. Install dependencies:
```bash
poetry install
```

### Running the Game

Start the Rummikub game:
```bash
poetry run python -m rummikub.main
```

### Running Tests

Execute the test suite:
```bash
poetry run pytest
```

Run tests with verbose output:
```bash
poetry run pytest -v
```

Run specific test file:
```bash
poetry run pytest tests/test_hint.py
```

### Development

The project uses:
- **OR-Tools** for constraint programming and AI hints
- **NetworkX** for graph-based sequence analysis
- **pytest** for testing

### Game Commands

- `a tegel1 tegel2 ...` - Place tiles (e.g., `a tr5 bb12`)
- `r tegel1 tegel2 ...` - Remove tiles
- `h` - Get AI hint
- `q` - Quit game

Tile format: `[location][color][number]`
- Location: `t` (table) or `b` (board)
- Color: `r` (red), `b` (blue), `g` (green), `z` (black)
- Number: 1-13