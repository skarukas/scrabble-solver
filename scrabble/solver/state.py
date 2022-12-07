from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Callable

from scrabble.solver.constraints import AffixConstraints
from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.util.scrabble_move import Move
from scrabble.util.scrabble_util import Direction
from scrabble.util.scrabble_util import PlacedTile
from scrabble.util.scrabble_util import Point


@dataclass
class State:
  """A state represents the context around an empty square and the move it is a part of.
  """

  letters_left: List[str]
  move: Move
  point: Point  # may not need point?
  constraints: AffixConstraints
  direction: Optional[Direction]
  touches_tile: bool

  def get_child_states_old(
      self, context: ScrabbleContext
  ) -> Tuple[List[TerminalState], List[State]]:
    terminal_states = []
    child_states = []
    # TODO: !!! fix! and can't explore two directions like
    #    X
    # ABCX
    #    X
    # Maybe get min and max of tiles based on MoveType, then explore in both directions.

    # If a direction is set, explore in that one. Otherwise explore in all
    # directions.
    directions = (
        [self.direction]
        if self.direction
        else [Direction.RIGHT, Direction.DOWN]
    )
    for direction in directions:  # Assume direction in [RIGHT, DOWN].
      for letter in self.letters_left:
        (
            is_valid_submove,
            is_valid_move,
        ) = self.constraints.check_constraints(letter, direction)
        if is_valid_submove:
          placed_tiles = [
              *self.move.placed_tiles,
              PlacedTile(letter, self.point),
          ]
          move = Move(placed_tiles)
          #print(f"{move} is a valid submove for direction {direction.name}")
          #print(f"(According to {self.constraints} at {self.point})")
          new_board = context.board.execute_move(move)

          inverse = direction.inverse()
          min_point = min(
              placed_tiles,
              key=_get_directional_coord(direction),
          ).location
          max_point = max(
              placed_tiles,
              key=_get_directional_coord(inverse),
          ).location

          # Explore by either adding to the end of the move or the beginning.
          for next_point in [
              min_point.move(inverse),
              max_point.move(direction),
          ]:
            if not context.board.can_place_tile_at(next_point):
              continue

            # Build the new state after putting down this letter.

            #print("Old constraints:", self.constraints)
            # TODO: Update constraints instead of generating from scratch.
            #print(f"trying to get constraints at {next_point} with {move}")
            constraints = AffixConstraints.get_constraints_at_point(
                new_board, context.dictionary, next_point
            )
            # constraints = self.constraints.update(
            #    next_point, direction, context
            # )

            print("Constraints for", next_point, constraints)
            letters_left = self.letters_left.copy()
            letters_left.remove(letter)  # Remove first occurence.
            state = State(
                letters_left, move, next_point, constraints, direction
            )
            child_states.append(state)
            if is_valid_move:
              terminal_state = TerminalState.create_from_state(state, context)
              terminal_states.append(terminal_state)

    return terminal_states, child_states

  def get_child_states(
      self, context: ScrabbleContext
  ) -> Tuple[List[TerminalState], List[State]]:
    # Explore in one direction.
    terminal_states = []
    child_states = []
    # If a direction is set, explore in that one. Otherwise explore in all
    # directions.
    directions = (
        [self.direction]
        if self.direction
        else [Direction.RIGHT, Direction.DOWN]
    )
    for direction in directions:  # Assume direction in [RIGHT, DOWN].
      for letter in self.letters_left:
        (
            is_valid_submove,
            is_valid_move,
        ) = self.constraints.check_constraints(letter, direction)
        if is_valid_submove:
          placed_tiles = [
              *self.move.placed_tiles,
              PlacedTile(letter, self.point),
          ]
          move = Move(placed_tiles)
          new_point = self.point.move(direction)
          if not context.board.can_place_tile_at(new_point):
            continue

          # Build the new state after putting down this letter.
          # TODO: Update constraints instead of generating from scratch.
          #print(f"trying to get constraints at {new_point} with {move}")
          new_board = context.board.execute_move(move)
          constraints = AffixConstraints.get_constraints_at_point(
              new_board, context.dictionary, new_point
          )
          touches_tile = self.touches_tile or context.board.point_touches_tiles(
              new_point
          )
          letters_left = self.letters_left.copy()
          letters_left.remove(letter)  # Remove first occurence.
          state = State(
              letters_left,
              move,
              new_point,
              constraints,
              direction,
              touches_tile,
          )
          child_states.append(state)
          if is_valid_move and touches_tile:
            terminal_state = TerminalState.create_from_state(state, context)
            terminal_states.append(terminal_state)

    return terminal_states, child_states


Score = dict


def _get_directional_coord(
    direction: Direction,
) -> Callable[[PlacedTile], float]:
  def _inner(tile: PlacedTile) -> float:
    if direction in (Direction.RIGHT, Direction.LEFT):
      return tile.location.x
    else:
      return tile.location.y

  return _inner

_DEFAULT_SCORE = {
    "total_score": 0
} 

@dataclass
class TerminalState(State):
  score: Score = field(default_factory=lambda: _DEFAULT_SCORE)

  @staticmethod
  def create_from_state(
      state: State, context: ScrabbleContext
  ) -> TerminalState:
    score = context.score_move(state.move)
    return TerminalState(
        state.letters_left,
        state.move,
        state.point,
        state.constraints,
        state.direction,
        False,
        score
    )
