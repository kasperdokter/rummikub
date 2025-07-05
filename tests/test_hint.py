
from rummikub.tile import Location, Tile


def test_simple_hint():
    from src.rummikub.hint import get_hint
    from src.rummikub.state import GameState

    state = GameState(
        tiles=[
            Tile(id=1, location=Location.TABLE, color='r', number=1),
            Tile(id=2, location=Location.TABLE, color='r', number=2),
            Tile(id=3, location=Location.TABLE, color='r', number=3),
            Tile(id=4, location=Location.BOARD, color='r', number=4)
        ]
    )
    hint = get_hint(state)
    print(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [state.tiles]

def test_simple_hint2():
    from src.rummikub.hint import get_hint
    from src.rummikub.state import GameState

    state = GameState(
        tiles=[
            Tile(id=1, location=Location.TABLE, color='b', number=6),
            Tile(id=2, location=Location.TABLE, color='b', number=8),
            Tile(id=3, location=Location.TABLE, color='b', number=9),
            Tile(id=4, location=Location.BOARD, color='b', number=7)
        ]
    )
    hint = get_hint(state)
    print(f"Hint: {hint}")
    assert state.tiles[3] in hint.playable
    assert hint.sequences == [sorted(state.tiles)]