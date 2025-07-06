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
    return f"{obj}_{label}" if label else repr(obj)


UniqueTile = tuple[int, Tile]


@dataclass
class Edge:
    source: UniqueTile
    target: UniqueTile
    type: EdgeType


def all_edges(state: GameState) -> Iterable[Edge]:
    """Generate all edges based on the tiles in the game state."""
    for t1 in enumerate(state.tiles):
        for t2 in enumerate(state.tiles):
            if t1[1].is_joker or t2[1].is_joker:
                yield Edge(t1, t2, EdgeType.SAME_COLOR)
                yield Edge(t1, t2, EdgeType.SAME_NUMBER)
            if t1[1].color == t2[1].color and t1[1].number + 1 == t2[1].number:
                yield Edge(t1, t2, EdgeType.SAME_COLOR)
            if t1[1].number == t2[1].number and t1[1].color < t2[1].color:
                yield Edge(t1, t2, EdgeType.SAME_NUMBER)


def adjacent_edges(tile: UniqueTile, state: GameState) -> Iterable[Edge]:
    """Get all edges adjacent to a tile."""
    for e in all_edges(state):
        if e.source == tile or e.target == tile:
            yield e


def adjacent_edges_of_same_type(edge: Edge, state: GameState) -> Iterable[Edge]:
    """Get all edges of the same type adjacent to a given edge."""
    for e in all_edges(state):
        if e.type == edge.type:
            if e.source == edge.target and e.target != edge.source:
                yield e
            if e.source != edge.target and e.target == edge.source:
                yield e


def build_model(
    state: GameState, first_turn: bool
) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    model = cp_model.CpModel()
    variables: dict[str, cp_model.IntVar] = {}

    def v(obj: object, label: str = "") -> cp_model.IntVar:
        v_name = varname(obj, label)
        v_obj = variables.get(v_name)
        if v_obj is None:
            v_obj = model.new_bool_var(v_name)
            variables[v_name] = v_obj
        return v_obj

    objective: list[cp_model.IntVar] = []

    # Every edge had adjacent edge on source or target tile of same edgetype
    for e1 in all_edges(state):
        model.add_at_least_one(
            v(e2) for e2 in adjacent_edges_of_same_type(e1, state)
        ).only_enforce_if(v(e1))

    if first_turn:
        tiles = enumerate(state.board)
    else:
        tiles = enumerate(state.tiles)

    for tile in tiles:

        # Every tile has at least one edge of each type
        model.add(sum(v(e) for e in adjacent_edges(tile, state)) <= 2)

        # Maximize the number of tiles played
        objective.append(v(tile, IN_SAME_NUMBER_SEQ))
        objective.append(v(tile, IN_SAME_COLOR_SEQ))

        # Every tile is connected to at most 1 type of edge
        # and tiles on the table must be played
        if not first_turn and tile[0] < len(state.table):
            model.add_exactly_one(
                v(tile, IN_SAME_NUMBER_SEQ), v(tile, IN_SAME_COLOR_SEQ)
            )
        else:
            model.add_at_most_one(
                v(tile, IN_SAME_NUMBER_SEQ), v(tile, IN_SAME_COLOR_SEQ)
            )

        for e in adjacent_edges(tile, state):
            if e.type == EdgeType.SAME_COLOR:
                model.add_implication(v(e), v(tile, IN_SAME_COLOR_SEQ))
                model.add_implication(v(tile, IN_SAME_NUMBER_SEQ), v(e).Not())
            if e.type == EdgeType.SAME_NUMBER:
                model.add_implication(v(e), v(tile, IN_SAME_NUMBER_SEQ))
                model.add_implication(v(tile, IN_SAME_COLOR_SEQ), v(e).Not())

        model.add(
            v(tile, IN_SAME_NUMBER_SEQ)
            <= sum(
                v(e)
                for e in adjacent_edges(tile, state)
                if e.type == EdgeType.SAME_NUMBER
            )
        )
        model.add(
            v(tile, IN_SAME_COLOR_SEQ)
            <= sum(
                v(e)
                for e in adjacent_edges(tile, state)
                if e.type == EdgeType.SAME_COLOR
            )
        )

    model.maximize(sum(objective))

    return model, variables


def get_playable_tiles(
    state: GameState,
    variables: dict[str, cp_model.IntVar],
    solver: cp_model.CpSolver,
    first_turn: bool,
) -> list[Tile]:

    def val(obj: object, label: str = "") -> bool:
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    playable: list[Tile] = []
    for tile in enumerate(state.tiles):
        if first_turn or tile[0] >= len(state.table):
            if val(tile, IN_SAME_COLOR_SEQ) or val(tile, IN_SAME_NUMBER_SEQ):
                playable.append(tile[1])
                logger.info(tile)

    return playable


def get_sequences(
    state: GameState, variables: dict[str, cp_model.IntVar], solver: cp_model.CpSolver
) -> list[list[Tile]]:

    def val(obj: object, label: str = "") -> bool:
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    # Build the graph from the solution
    graph = nx.Graph()
    for e in all_edges(state):
        if val(e):
            graph.add_edge(e.source, e.target)
            logger.info(e)

    # The sequences are the connected components of the graph
    sequences: list[list[Tile]] = []
    for component in nx.connected_components(graph):
        seq: list[UniqueTile] = sorted(
            component, key=lambda t: (t[1].color, t[1].number)
        )
        sequences.append([t[1] for t in seq])

    return sequences


def get_hint(state: GameState, first_turn: bool = False) -> Hint:
    model, variables = build_model(state, first_turn)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    logger.info(f"Solver status: {solver.StatusName(status)}")
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # for v, ivar in variables.items():
        #     logger.info(f'{v}: {solver.Value(ivar)}')
        return Hint(
            playable=get_playable_tiles(state, variables, solver, first_turn),
            sequences=get_sequences(state, variables, solver),
        )

    return Hint(playable=[], sequences=[])
