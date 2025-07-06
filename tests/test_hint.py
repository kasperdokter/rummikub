import logging

from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile

logger = logging.getLogger(__name__)


def test_simple_hint() -> None:
    state = GameState(
        table=[
            Tile(color="r", number=1, is_joker=False),
            Tile(color="r", number=2, is_joker=False),
            Tile(color="r", number=4, is_joker=False),
        ],
        board=[
            Tile(color="r", number=3, is_joker=False),
        ],
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_simple_hint2() -> None:
    state = GameState(
        table=[
            Tile(color="g", number=7, is_joker=False),
            Tile(color="b", number=7, is_joker=False),
        ],
        board=[
            Tile(color="z", number=7, is_joker=False),
            Tile(color="r", number=7, is_joker=False),
        ],
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[2] in hint.playable
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_joker() -> None:
    state = GameState(
        table=[
            Tile(color="r", number=1, is_joker=False),
            Tile(color="r", number=2, is_joker=False),
            Tile(color="r", number=4, is_joker=False),
        ],
        board=[
            Tile(color="z", number=0, is_joker=True),
        ],
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_first_turn() -> None:
    state = GameState(
        table=[],
        board=[
            Tile(color="r", number=1, is_joker=False),
            Tile(color="r", number=2, is_joker=False),
            Tile(color="r", number=3, is_joker=False),
        ],
    )
    hint = get_hint(state, first_turn=True)
    logger.info(f"Hint: {hint}")
    assert state.tiles[0] in hint.playable
    assert state.tiles[1] in hint.playable
    assert state.tiles[2] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]


def test_duplicates() -> None:
    state = GameState(
        table=[
            Tile(color="r", number=1, is_joker=False),
            Tile(color="r", number=2, is_joker=False),
            Tile(color="r", number=3, is_joker=False),
        ],
        board=[
            Tile(color="r", number=2, is_joker=False),
        ],
    )
    hint = get_hint(state)
    logger.info(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert state.tiles[4] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]
