import logging

from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile

logger = logging.getLogger(__name__)


def get_state(table: str, board: str) -> GameState:
    """Helper function to create a GameState from table and board strings."""
    table_tiles = [t for s in table.split() for t in Tile.parse(s)]
    board_tiles = [t for s in board.split() for t in Tile.parse(s)]
    return GameState(table=table_tiles, board=board_tiles)


def test_simple_hint() -> None:
    state = get_state(
        table="r1 r2 r4",
        board="r3",
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_simple_hint2() -> None:
    state = get_state(
        table="g7 b7",
        board="z7 r7",
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[2] in hint.playable
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_joker() -> None:
    state = get_state(
        table="r1 r2 r4",
        board="?",
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_first_turn_ok() -> None:
    state = get_state(
        table="",
        board="r9 r10 r11",
    )
    hint = get_hint(state, first_turn=True)
    logger.info(f"Hint: {hint}")
    assert all(tile in hint.playable for tile in state.tiles)
    assert hint.sequences == [sorted(state.tiles)]


def test_first_turn_insufficient() -> None:
    state = get_state(
        table="",
        board="r1 r2 r3",
    )
    hint = get_hint(state, first_turn=True)
    logger.info(f"Hint: {hint}")
    assert not hint.playable


def test_duplicates() -> None:
    state = get_state(
        table="r1 r2 r3",
        board="r2",
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert not hint.playable
