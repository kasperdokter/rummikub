from dataclasses import dataclass, field

from rummikub.tile import Tile


@dataclass
class GameState:
    table: list[Tile] = field(default_factory=list)
    board: list[Tile] = field(default_factory=list)
    first_turn: bool = True

    @property
    def tiles(self) -> list[Tile]:
        """Combine tiles from the table and board."""
        if self.first_turn:
            return self.board
        return self.table + self.board

    @property
    def number_of_tile_on_table(self) -> int:
        """Number of tiles that are on the table."""
        if self.first_turn:
            return 0
        return len(self.table)

    def table_str(self) -> str:
        """Return a string representation of the table tiles."""
        return " ".join(str(tile) for tile in sorted(self.table))

    def board_str(self, pretty: bool = True) -> str:
        """Return a string representation of the board tiles."""
        return " ".join(str(tile) for tile in sorted(self.board))

    def __repr__(self) -> str:
        return (
            f'State(table="{self.table_str()}", '
            f'board="{self.board_str()}", '
            f"first_turn={self.first_turn}"
        )
