from dataclasses import dataclass
from typing import Iterable


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
    def parse(cls, tile_str: str) -> Iterable["Tile"]:
        """Parse a tile from string format like 'r5' or 'b12'"""
        if tile_str == "?":
            yield cls(color="r", number=0, is_joker=True)
            return

        try:
            first_digit_idx = next(
                (i for i, c in enumerate(tile_str) if c.isdigit()), None
            )
            assert first_digit_idx is not None, "Tegel moet een cijfer bevatten"

            color_chars = tile_str[:first_digit_idx]
            number_parts = tile_str[first_digit_idx:].split("-")

            assert color_chars, "Tegel moet een kleur bevatten"
            assert all(c in "rbgz" for c in color_chars), "Ongeldige kleur in tegel"
            assert len(number_parts) in [1, 2], "Tegels hebben één of twee nummers"

            numbers = [int(part) for part in number_parts]

            assert all(
                1 <= number <= 13 for number in numbers
            ), "Nummers moeten tussen 1 en 13 liggen"

            if len(numbers) == 1:
                numbers.append(numbers[0])

            assert numbers[0] <= numbers[1], "Nummers moeten oplopend zijn"

            for color_char in color_chars:
                for number in range(numbers[0], numbers[1] + 1):
                    yield cls(color=color_char, number=number, is_joker=False)

        except (ValueError, AssertionError) as e:
            raise ValueError(f"Ongeldige tegel {tile_str}: {e}")
