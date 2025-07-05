from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile


def main():
    state = GameState()
    print()
    print("Welkom bij Rummikub!")
    print()
    print("Je kunt tegels plaatsen in de vorm van 'tr5' (op tafel -> rood 5) of 'bb12' (op bordje -> blauw 12).")
    print("Typ 'a tegel1 tegel2 ...' om tegels te plaatsen.")
    print("Typ 'r tegel1 tegel2 ...' om tegels weg te halen.")
    print("Typ 'h' om een suggestie te krijgen.")
    print("Typ 'q' om te stoppen.")

    while True:
        print()
        print(state)
        print()
        while True:
            try:
                response = input(">>> ").strip()
                args = response.lower().split()
                assert args, "Geen commando"
                if args[0] == 'q':
                    return
                elif args[0] == 'h':
                    hint = get_hint(state)
                    if hint.playable:
                        playable_tiles = ' '.join(str(tile) for tile in hint.playable)
                        print(f"Je kan de volgende tegels spelen: {playable_tiles}")
                        print("Maak de volgende rijtjes:")
                        for i, seq in enumerate(hint.sequences):
                            print(i+1, ' '.join(str(tile) for tile in seq))
                    else:
                        print("Je moet kopen.")
                elif args[0] == 'a':
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.tiles.append(tile)
                elif args[0] == 'r':
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.tiles.remove(tile)
                else:
                    print("Ongeldige invoer. Probeer het opnieuw.")
                break
            except (ValueError, AssertionError) as e:
                print(f"Er is iets misgegaan ({e}). Probeer het opnieuw.")


if __name__ == "__main__":
    main()
