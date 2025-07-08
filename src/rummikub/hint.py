import logging
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

import networkx as nx
from ortools.sat.python import cp_model

from rummikub.state import GameState
from rummikub.tile import Tile

logger = logging.getLogger(__name__)


@dataclass
class Hint:
    playable: list[Tile]
    sequences: list[list[Tile]]


class EdgeType(Enum):
    SAME_COLOR = 0
    SAME_NUMBER = 1


IN_SAME_NUMBER_SEQ = "in_same_number_sequence"
IN_SAME_COLOR_SEQ = "in_same_color_sequence"


def varname(obj: object, label: str = "") -> str:
    """Generate a variable name based on the object and label."""
    return f"{repr(obj)}_{label}" if label else repr(obj)


UniqueTile = tuple[int, Tile]


@dataclass(frozen=True)
class Edge:
    source: UniqueTile
    target: UniqueTile

    def __str__(self) -> str:
        return f"{self.source[1]} -> {self.target[1]}"

    def __repr__(self) -> str:
        return f"{self.source} -> {self.target}"


def valid_edge_colors(t1: UniqueTile, t2: UniqueTile) -> set[int]:
    """Check if an edge between two tiles is valid."""
    if t1 == t2:
        return set()
    if t1[1].is_joker and t2[1].is_joker:
        return set(range(1, 15))
    if t1[1].is_joker and not t2[1].is_joker:
        return {t2[1].number, 14}
    if not t1[1].is_joker and t2[1].is_joker:
        return {t1[1].number, 14}
    if t1[1].color == t2[1].color and t1[1].number + 1 == t2[1].number:
        return {14}
    if t1[1].number == t2[1].number and t1[1].color < t2[1].color:
        return {t1[1].number}
    return set()


def valid_sequence_colors(
    t1: UniqueTile, t2: UniqueTile, t3: UniqueTile
) -> Iterable[int]:
    colors = valid_edge_colors(t1, t2) & valid_edge_colors(t2, t3)
    for c in colors:
        if not t1[1].is_joker:
            if not t3[1].is_joker:
                if c == 14:
                    if t1[1].number + 2 != t3[1].number:
                        continue
                    if t1[1].color != t3[1].color:
                        continue
                else:
                    if t1[1].number != t3[1].number:
                        continue
                    if t1[1].color >= t3[1].color:
                        continue
        yield c


def is_adjacent(edge1: Edge, edge2: Edge) -> bool:
    """Check if two edges are adjacent."""
    return edge1.target == edge2.source or edge1.source == edge2.target


def build_model(
    state: GameState,
) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    model = cp_model.CpModel()
    variables: dict[str, cp_model.IntVar] = {}

    def v(obj: object, label: str = "", lb: int = 0, ub: int = 14) -> cp_model.IntVar:
        v_name = varname(obj, label)
        v_obj = variables.get(v_name)
        if v_obj is None:
            v_obj = model.new_int_var(lb, ub, v_name)
            variables[v_name] = v_obj
        return v_obj

    tiles = list(enumerate(state.tiles))

    edges = [Edge(t1, t2) for t1 in tiles for t2 in tiles if valid_edge_colors(t1, t2)]

    logger.debug("Graph edges:")
    for e in edges:
        logger.debug(e)

    # Ensure sequences are of length at least 3
    for e in edges:
        model.add(v(e) <= sum(v(adj) for adj in edges if is_adjacent(e, adj)))

    # Ensure the graph is valid at every tile
    for tile in tiles:

        logger.debug(f"Validity at tile {tile}")
        adjacent_edges = [e for e in edges if e.source == tile or e.target == tile]
        logger.debug(adjacent_edges)
        if not adjacent_edges:
            continue

        assignments = []

        # Tiles on the board may not be in a sequence
        if tile[0] >= state.number_of_tile_on_table:
            a = [0 for _ in adjacent_edges]
            assignments.append(a)
            logger.debug(f"{a} {tile} not played")

        # Case 1: tile is in the middle of a sequence
        for left in tiles:
            for right in tiles:
                for c in valid_sequence_colors(left, tile, right):
                    a = [
                        c if e == Edge(left, tile) or e == Edge(tile, right) else 0
                        for e in adjacent_edges
                    ]
                    assignments.append(a)
                    logger.debug(f"{a} {left[1]} -> {tile[1]} -> {right[1]}")

        # Case 2: tile is the start of a sequence
        for left in tiles:
            for c in valid_edge_colors(left, tile):
                a = [c if e == Edge(left, tile) else 0 for e in adjacent_edges]
                assignments.append(a)
                logger.debug(f"{a} {left[1]} -> {tile[1]}")

        # Case 3: tile is the end of a sequence
        for right in tiles:
            for c in valid_edge_colors(tile, right):
                a = [c if e == Edge(tile, right) else 0 for e in adjacent_edges]
                assignments.append(a)
                logger.debug(f"{a} {tile[1]} -> {right[1]}")

        model.add_allowed_assignments(
            [v(e) for e in adjacent_edges],
            assignments,
        )

    # B = len(edges) + 1

    objective = 0

    # Maximize the number of tiles played
    for tile in tiles:
        if tile[0] >= state.number_of_tile_on_table:
            obj_var = v(tile, label="obj", lb=0, ub=1)
            objective += obj_var
            model.add(
                obj_var
                <= sum(v(e) for e in edges if e.source == tile or e.target == tile)
            )

    # Then, make as many connections as possible
    # for e in edges:
    #     objective += v(e)

    logger.debug(f"objective: {objective}")
    model.maximize(objective)

    return model, variables


def get_playable_tiles(
    state: GameState,
    variables: dict[str, cp_model.IntVar],
    solver: cp_model.CpSolver,
) -> list[Tile]:

    def val(obj: object, label: str = "") -> bool:
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    # Get all edges with an edge
    used_tiles: set[UniqueTile] = set()
    for t1 in enumerate(state.tiles):
        for t2 in enumerate(state.tiles):
            edge = Edge(t1, t2)
            if val(edge):
                used_tiles.add(t1)
                used_tiles.add(t2)

    return sorted(t[1] for t in used_tiles if t[0] >= state.number_of_tile_on_table)


def get_sequences(
    state: GameState,
    variables: dict[str, cp_model.IntVar],
    solver: cp_model.CpSolver,
) -> list[list[Tile]]:

    def val(obj: object, label: str = "") -> bool:
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    # Build the graph from the solution
    graph = nx.Graph()
    for t1 in enumerate(state.tiles):
        for t2 in enumerate(state.tiles):
            e = Edge(t1, t2)
            if val(e):
                graph.add_edge(e.source, e.target)

    # The sequences are the connected components of the graph
    sequences: list[list[Tile]] = []
    for component in nx.connected_components(graph):
        seq: list[UniqueTile] = sorted(
            component, key=lambda t: (t[1].color, t[1].number)
        )
        sequences.append([t[1] for t in seq])

    return sequences


def total(tiles: Iterable[Tile]) -> int:
    return sum(tile.number for tile in tiles if not tile.is_joker)


def get_hint(state: GameState) -> Hint:
    logger.debug(f"Getting hint for state: {state}")
    model, variables = build_model(state)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    logger.debug(f"Solver status: {solver.StatusName(status)}")
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):

        logger.debug("Solution:")
        for v_name, v_obj in variables.items():
            logger.debug(f"{v_name}: {solver.Value(v_obj)}")

        playable = get_playable_tiles(state, variables, solver)

        if not state.first_turn or total(playable) >= 30:
            return Hint(
                playable=playable,
                sequences=get_sequences(state, variables, solver),
            )

    return Hint(playable=[], sequences=[])
