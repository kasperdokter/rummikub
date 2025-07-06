from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    color: str
    number: int
    is_joker: bool

    def __lt__(self, other: "Tile") -> bool:
        """Compare tiles first by color, then by number."""
        if (self.color, self.number) < (other.color, other.number):
            return True
        return False

    def __repr__(self) -> str:
        if self.is_joker:
            return "?"
        elif self.color == "r":
            return f"\033[31m{self.number}\033[0m"
        elif self.color == "b":
            return f"\033[34m{self.number}\033[0m"
        elif self.color == "g":
            return f"\033[33m{self.number}\033[0m"
        return f"\033[32m{self.number}\033[0m"

    @classmethod
    def from_string(cls, tile_str: str) -> "Tile":
        """Parse a tile from string format like 'r5' or 'b12'"""
        if tile_str == "?":
            return cls(color="r", number=0, is_joker=True)

        if len(tile_str) < 2:
            raise ValueError(f"Ongeldige tegel: {tile_str}")

        color_char = tile_str[0]
        number_str = tile_str[1:]

        try:
            assert (
                color_char in "rbgz"
            ), "Kleur moet rood (r), blauw (b), groen (g), of zwart (z) zijn."
            number = int(number_str)
            assert 1 <= number <= 13, "Nummer moet tussen 1 en 13 liggen."
        except (ValueError, IndexError, AssertionError):
            raise ValueError(f"Ongeldige tegel: {tile_str}")

        return cls(color=color_char, number=number, is_joker=False)
