from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile

PLAY = "p"
PUT_TABLE = "t"
TAKE_TABLE = "rt"
TAKE_BOARD = "rb"
RESET = "z"
EXIT_GAME = "q"


def main() -> None:
    state = GameState()
    must_buy = False
    hinted = []
    print()
    print("Welkom bij Rummikub!")
    print()
    print("Typ de volgende commando's om te spelen:")
    print(f" - \033[93m{PLAY:<8}\033[0m Verplaats tegels van je bordje naar de tafel.")
    print(f" - \033[93m{PUT_TABLE:<8}\033[0m Plaats tegels op de tafel.")
    print(f" - \033[93m{TAKE_TABLE:<8}\033[0m Verwijder tegels van de tafel.")
    print(f" - \033[93m{TAKE_BOARD:<8}\033[0m Verwijder tegels van je bordje.")
    print(f" - \033[93m{RESET:<8}\033[0m Reset de tafel en het bordje.")
    print(f" - \033[93m{EXIT_GAME:<8}\033[0m Stop het spel.")

    while True:

        print()
        print("Tafel :", state.table_str())
        print("Bord  :", state.board_str())
        print()

        if must_buy:
            hint = get_hint(state)
            if hint.playable:
                hinted = hint.playable
                playable_tiles = " ".join(str(t) for t in sorted(hint.playable))
                print(f"\tJe kan de volgende tegels spelen: {playable_tiles}")
                print("\tMaak de volgende rijtjes:")
                sorted_seq = sorted(
                    hint.sequences, key=lambda s: (s[0].number, s[0].color)
                )
                for i, seq in enumerate(sorted_seq):
                    print(f"\t  {i + 1}) {' '.join(str(tile) for tile in seq)}")
            else:
                print("\tJe moet kopen.")
        else:
            print("\tJe moet kopen.")
        print()

        must_buy = False

        while True:
            try:
                response = input(">>> ").strip()
                args = response.lower().split()
                assert args, "Geen commando"
                if args[0] == EXIT_GAME:
                    return
                elif args[0] == PUT_TABLE:
                    for tile_str in args[1:]:
                        for tile in Tile.parse(tile_str):
                            state.table.append(tile)
                elif args[0] == TAKE_TABLE:
                    for tile_str in args[1:]:
                        for tile in Tile.parse(tile_str):
                            state.table.remove(tile)
                elif args[0] == TAKE_BOARD:
                    for tile_str in args[1:]:
                        for tile in Tile.parse(tile_str):
                            state.board.remove(tile)
                elif args[0] == PLAY:
                    must_buy = True
                    state.first_turn = False
                    if len(args) == 1:
                        for tile in hinted:
                            state.board.remove(tile)
                            state.table.append(tile)
                    else:
                        for tile_str in args[1:]:
                            for tile in Tile.parse(tile_str):
                                state.board.remove(tile)
                                state.table.append(tile)
                elif args[0] == RESET:
                    state.table.clear()
                    state.board.clear()
                    state.first_turn = True
                    hinted = []
                else:
                    for tile_str in args:
                        for tile in Tile.parse(tile_str):
                            state.board.append(tile)
                break
            except (ValueError, AssertionError) as e:
                print(f"Er is iets misgegaan ({e}). Probeer het opnieuw.")
            except KeyboardInterrupt:
                print("\nTot ziens!")
                return


if __name__ == "__main__":
    main()
