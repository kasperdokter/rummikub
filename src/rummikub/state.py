from dataclasses import dataclass, field

from rummikub.tile import Tile


@dataclass
class GameState:
    table: list[Tile] = field(default_factory=list)
    board: list[Tile] = field(default_factory=list)

    @property
    def tiles(self) -> list[Tile]:
        """Combine tiles from the table and board."""
        return self.table + self.board

    def __repr__(self) -> str:
        table = " ".join(str(t) for t in sorted(self.table))
        board = " ".join(str(t) for t in sorted(self.board))
        return f"State(table={table}, board={board})"
