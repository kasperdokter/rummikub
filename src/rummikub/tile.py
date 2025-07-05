from dataclasses import dataclass
from enum import Enum


class Location(Enum):
    TABLE = 't'
    BOARD = 'b'

tile_id = 0

def get_fresh_tile_id() -> int:
    """Generate a new unique tile ID."""
    global tile_id
    tile_id += 1
    return tile_id


@dataclass(frozen=True)
class Tile:
    id: int
    location: Location
    color: str
    number: int

    def __lt__(self, other: 'Tile') -> bool:
        """Compare tiles first by color, then by number."""
        if self.color == other.color:
            return self.number < other.number
        if self.number == other.number:
            return self.color < other.color
        return False

    def __repr__(self):
        return f"{self.location.value}{self.color}{self.number}-{self.id}"
    
    def name(self) -> str:
        return f"{self.color}{self.number}"
    
    @classmethod
    def from_string(cls, tile_str: str) -> 'Tile':
        """Parse a tile from string format like 'R5' or 'B12'"""
        if len(tile_str) < 3:
            raise ValueError(f"Ongeldige tegel: {tile_str}")
        
        loc_char = tile_str[0]
        color_char = tile_str[1]
        number_str = tile_str[2:]
        
        try:
            assert loc_char in 'tb', "Tegel moet op tafel (t) of je bordje (b) liggen."
            assert color_char in 'rbgz', "Kleur moet rood (r), blauw (b), groen (g), of zwart (z) zijn."
            number = int(number_str)
            assert 1 <= number <= 13, "Nummer moet tussen 1 en 13 liggen."
        except (ValueError, IndexError, AssertionError):
            raise ValueError(f"Ongeldige tegel: {tile_str}")
        
        return cls(
            id=get_fresh_tile_id(), 
            location=Location(loc_char), 
            color=color_char, 
            number=number
        )