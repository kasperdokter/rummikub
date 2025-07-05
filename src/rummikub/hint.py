from dataclasses import dataclass
from typing import Iterable

from ortools.sat.python import cp_model
import networkx as nx

from rummikub.state import GameState
from rummikub.tile import Tile, Location
from enum import Enum


@dataclass
class Hint:
    playable: list[Tile]
    sequences: list[list[Tile]]

class EdgeType(Enum):
    SAME_COLOR = 0
    SAME_NUMBER = 1

IN_SAME_NUMBER_SEQ = 'in_same_number_sequence'
IN_SAME_COLOR_SEQ = 'in_same_color_sequence'

def varname(obj, label=None) -> str:
    """Generate a variable name based on the object and label."""
    return f'{obj}_{label}' if label else repr(obj)
    
@dataclass
class Edge:
    source: Tile
    target: Tile
    type: EdgeType


def all_edges(state: GameState) -> Iterable[Edge]:
    """Generate all edges based on the tiles in the game state."""
    for t1 in state.tiles:
        for t2 in state.tiles:
            if t1.color == t2.color and t1.number + 1 == t2.number:
                yield Edge(t1, t2, EdgeType.SAME_COLOR)
            if t1.number == t2.number and t1.color < t2.color:
                yield Edge(t1, t2, EdgeType.SAME_NUMBER)

def adjacent_edges(tile: Tile, state: GameState) -> Iterable[Edge]:
    """Get all edges adjacent to a tile."""
    for e in all_edges(state):
        if e.source == tile or e.target == tile:
            yield e

def adjacent_edges_of_same_type(edge: Edge, state: GameState) -> Iterable[Edge]:
    """Get all edges of the same type adjacent to a given edge."""
    for e in all_edges(state):
        if e.type == edge.type and (e.source == edge.target or e.target == edge.source):
            yield e

def build_model(state: GameState):
    model = cp_model.CpModel()
    variables: dict[str, cp_model.IntVar] = {}

    def v(obj, label='') -> cp_model.IntVar:
        v_name = varname(obj, label)
        v_obj = variables.get(v_name)
        if v_obj is None:
            v_obj = model.new_bool_var(v_name)
            variables[v_name] = v_obj
        return v_obj

    objective = []

    # Every edge had adjacent edge on source or target tile of same edgetype
    for e1 in all_edges(state):
        model.add_at_least_one(v(e2) for e2 in adjacent_edges_of_same_type(e1, state))

    # Every tile is connected to at most 1 type of edge
    for tile in state.tiles:

        # Maximize the number of tiles played
        objective.append(v(tile, IN_SAME_NUMBER_SEQ))
        objective.append(v(tile, IN_SAME_COLOR_SEQ))

        # Every tile is connected to at most 1 type of edge and tiles on the table must be played
        if tile.location == Location.TABLE:
            model.add_exactly_one(v(tile, IN_SAME_NUMBER_SEQ), v(tile, IN_SAME_COLOR_SEQ))
        else:    
            model.add_at_most_one(v(tile, IN_SAME_NUMBER_SEQ), v(tile, IN_SAME_COLOR_SEQ))

        # Define the tile variables
        for e in adjacent_edges(tile, state):
            if e.type == EdgeType.SAME_COLOR:
                model.add_implication(v(e), v(tile, IN_SAME_COLOR_SEQ))
                model.add_implication(v(tile, IN_SAME_NUMBER_SEQ), v(e).Not())
            if e.type == EdgeType.SAME_NUMBER:
                model.add_implication(v(e), v(tile, IN_SAME_NUMBER_SEQ))
                model.add_implication(v(tile, IN_SAME_COLOR_SEQ), v(e).Not())

        for tile in state.tiles:
            model.add( 
                v(tile, IN_SAME_NUMBER_SEQ) <= sum(
                    v(e) for e in adjacent_edges(tile, state) 
                    if e.type == EdgeType.SAME_NUMBER
                )
            )
            model.add( 
                v(tile, IN_SAME_COLOR_SEQ) <= sum(
                    v(e) for e in adjacent_edges(tile, state) 
                    if e.type == EdgeType.SAME_COLOR
                )
            )

    model.maximize(sum(objective))

    return model, variables

def get_playable_tiles(state: GameState, variables: dict[str, cp_model.IntVar], solver: cp_model.CpSolver) -> list[Tile]:

    def val(obj, label=''):
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    playable = []
    for tile in state.tiles:
        if tile.location == Location.BOARD:
            if val(tile, IN_SAME_COLOR_SEQ) or val(tile, IN_SAME_NUMBER_SEQ):
                playable.append(tile)

    return playable

def get_sequences(state: GameState, variables: dict[str, cp_model.IntVar], solver: cp_model.CpSolver):

    def val(obj, label=''):
        """Get the value of a variable."""
        ivar = variables.get(varname(obj, label))
        return solver.Value(ivar) > 0.5 if ivar is not None else False

    # Build the graph from the solution
    graph = nx.Graph()
    for e in all_edges(state):
        if val(e):
            graph.add_edge(e.source, e.target, type=e.type)
            print(e)

    # The sequences are the connected components of the graph
    sequences = []
    for component in nx.connected_components(graph):
        seq: list[Tile] = sorted(component, key=lambda t: (t.color, t.number))
        sequences.append(seq)

    return sequences

def get_hint(state: GameState) -> Hint:
    model, variables = build_model(state)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    print(f'Solver status: {solver.StatusName(status)}')
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for v, ivar in variables.items():
            print(f'{v}: {solver.Value(ivar)}')

        return Hint(
            playable=get_playable_tiles(state, variables, solver), 
            sequences=get_sequences(state, variables, solver)
        )

    return Hint(playable=[], sequences=[])
