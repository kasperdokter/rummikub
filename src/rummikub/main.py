from rummikub.hint import get_hint
from rummikub.state import GameState
from rummikub.tile import Tile


def main() -> None:
    state = GameState()
    print()
    print("Welkom bij Rummikub!")
    print()
    print("Je kunt tegels plaatsen in de vorm van 'r5' (rood 5) of 'b12' (blauw 12).")
    print(
        "Typ 'speel tegel1 tegel2 ...' "
        "om tegels van je bordje op de tafel te plaatsen."
    )
    print("Typ 'leg tegel1 tegel2 ...' " "om tegels op de tafel te plaatsen.")
    print("Typ 'koop tegel1 tegel2 ...' om tegels op je bordje te plaatsen.")
    print("Typ 'vantafel tegel1 tegel2 ...' om tegels van de tafel te halen.")
    print("Typ 'vanbord tegel1 tegel2 ...' om tegels van je bordje te halen.")
    print("Typ 'hint' om een suggestie te krijgen.")
    print("Typ 'stop' om te stoppen.")

    while True:
        print()
        print(state)
        print()
        while True:
            try:
                response = input(">>> ").strip()
                args = response.lower().split()
                assert args, "Geen commando"
                if args[0] == "stop":
                    return
                elif args[0] == "hint":
                    hint = get_hint(state)
                    if hint.playable:
                        playable_tiles = " ".join(str(tile) for tile in hint.playable)
                        print(f"Je kan de volgende tegels spelen: {playable_tiles}")
                        print("Maak de volgende rijtjes:")
                        for i, seq in enumerate(hint.sequences):
                            print(i + 1, " ".join(str(tile) for tile in seq))
                    else:
                        print("Je moet kopen.")
                elif args[0] == "leg":
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.table.append(tile)
                elif args[0] == "koop":
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.board.append(tile)
                elif args[0] == "rt":
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.table.remove(tile)
                elif args[0] == "rb":
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.board.remove(tile)
                elif args[0] == "speel":
                    for tile_str in args[1:]:
                        tile = Tile.from_string(tile_str)
                        state.board.remove(tile)
                        state.table.append(tile)
                else:
                    print("Ongeldige invoer. Probeer het opnieuw.")
                break
            except (ValueError, AssertionError) as e:
                print(f"Er is iets misgegaan ({e}). Probeer het opnieuw.")
            except KeyboardInterrupt:
                print("\nTot ziens!")
                return


if __name__ == "__main__":
    main()
