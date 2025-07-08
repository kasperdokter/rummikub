import logging

from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile

logger = logging.getLogger(__name__)


def tiles(tile_str: str) -> list[Tile]:
    """Parse a string of tiles into a list of Tile objects."""
    return sorted([t for s in tile_str.split() for t in Tile.parse(s)])


def get_state(table: str, board: str, first_turn: bool = True) -> GameState:
    """Helper function to create a GameState from table and board strings."""
    return GameState(table=tiles(table), board=tiles(board), first_turn=first_turn)


def test_simple_hint() -> None:
    state = get_state(
        table="r1 r2 r4",
        board="r3",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_simple_hint2() -> None:
    state = get_state(
        table="g7 b7",
        board="z7 r7",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert state.tiles[2] in hint.playable
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_joker() -> None:
    state = get_state(
        table="r1 r2 r4",
        board="?",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_joker2() -> None:
    state = get_state(
        table="r1 r3",
        board="? g1 g3",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert state.tiles[2] in hint.playable
    assert hint.sequences in [
        [sorted(Tile.parse_all("? r1 r3"))],
        [sorted(Tile.parse_all("? g1 g3"))],
    ]


def test_first_turn_ok() -> None:
    state = get_state(
        table="",
        board="r9 r10 r11",
        first_turn=True,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert all(tile in hint.playable for tile in state.tiles)
    assert hint.sequences == [sorted(state.tiles)]


def test_first_turn_insufficient() -> None:
    state = get_state(
        table="",
        board="r1 r2 r3",
        first_turn=True,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert not hint.playable


def test_duplicates() -> None:
    state = get_state(
        table="r1 r2 r3",
        board="r2",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert not hint.playable


def test_incomplete() -> None:
    state = get_state(
        table="",
        board="b1 b3-5 b7 r4 r5 r6 r7 r8 r8 r13 z2 z4 z5 z7 z9 z12 g6 g11 g13",
        first_turn=True,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert len(hint.playable) == 9


def test_invalid_sequence() -> None:
    state = get_state(
        table="b1-5 g4-6 g9 r3-9 z2-5 z9",
        board="? b1 b7 g2 g2 g9 g11 g13 r1 r8 r13 z3 z7 z8 z12 z12",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(state)
    logger.info(hint)
    assert len(hint.playable) == 4


def test_play_maximal() -> None:
    state = get_state(
        table="b1-3",
        board="b4 b5 r4 z4",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(f"{state}")
    logger.info(f"{hint}")
    assert hint.playable == tiles("brz4")


def test_play_all() -> None:
    state = get_state(
        table="",
        board="? ? b1 b2 b2-4 b4 b5 b5-7 b7-9 b12 b12 b13 b13 g2 g2 g3 g3 g4 g4 g5 g5 "
        "g6 g6 g7 g7 g9 g9 g10 g10 g11 g12 g12 g13 g13 r1 r2 r2 r3 r4 r5 r5 r6 r6 "
        "r7 r7 r8 r8 r9 r9 r10 r11 r11 r12 r12 r13 z2 z2 z3 z3 z4 z4 z5 z7 z7 z8 "
        "z8 z9 z11 z12 z12 z13 z13",
        first_turn=False,
    )
    hint = get_hint(state)
    logger.info(f"{state}")
    logger.info(f"{hint}")
    assert hint.playable == state.tiles
