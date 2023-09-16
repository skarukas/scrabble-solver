from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.scrabble_dictionary import ScrabbleDictionary
from scrabble.context.scrabble_board import ScrabbleBoard
from scrabble.util.scrabble_util import Direction
from scrabble.util.scrabble_util import Point


class InvalidAffixError(ValueError):
  pass


@dataclass
class _AffixConstraint:
  affix: str
  trie: ScrabbleDictionary.Trie

  @staticmethod
  def create_prefix_constraint(
      dictionary: ScrabbleDictionary, prefix: str
  ) -> _AffixConstraint:
    trie = dictionary.prefix_tree
    for c in prefix:
      if c in trie:
        trie = trie[c]
      else:
        raise InvalidAffixError(
            f"The constraint cannot be created because {prefix} is not a valid"
            " prefix to any words in the given dictionary."
        )

    return _AffixConstraint(prefix, trie)

  @staticmethod
  def create_suffix_constraint(
      dictionary: ScrabbleDictionary, suffix: str
  ) -> _AffixConstraint:
    trie = dictionary.suffix_tree
    for c in reversed(suffix):
      if c in trie:
        trie = trie[c]
      else:
        raise InvalidAffixError(
            f"The constraint cannot be created because {suffix} is not a valid"
            " suffix to any words in the given dictionary."
        )

    return _AffixConstraint(suffix, trie)


@dataclass
class AffixConstraints:
  _directional_constraints: Dict[Direction, _AffixConstraint]
  _dictionary: ScrabbleDictionary

  @staticmethod
  def create_if_valid(
      dictionary: ScrabbleDictionary,
      lr_prefix: Optional[str] = None,
      lr_suffix: Optional[str] = None,
      ud_prefix: Optional[str] = None,
      ud_suffix: Optional[str] = None,
  ) -> AffixConstraints:
    """Tries to produce an AffixConstraints object given the prefix and suffix

    constraints provided. If any of the given strings cannot be affixes (for
    example, `lr_prefix="ZOOS"`) to words in the given dictionary, this method
    will raise an `InvalidAffixError`. The letters within each string should be
    in reading order.
    """
    constraint_dict: Dict[Direction, _AffixConstraint] = {}
    direction_pairings = [
        (lr_prefix, Direction.LEFT, _AffixConstraint.create_prefix_constraint),
        (lr_suffix, Direction.RIGHT, _AffixConstraint.create_suffix_constraint),
        (ud_prefix, Direction.UP, _AffixConstraint.create_prefix_constraint),
        (ud_suffix, Direction.DOWN, _AffixConstraint.create_suffix_constraint),
    ]
    for affix, direction, create_constraint in direction_pairings:
      if affix:
        constraint_dict[direction] = create_constraint(dictionary, affix)

    return AffixConstraints(constraint_dict, dictionary)

  @staticmethod
  def get_constraints_at_point(
      board: ScrabbleBoard, dictionary: ScrabbleDictionary, coord: Point
  ) -> Optional[AffixConstraints]:
    """If the given coordinate is an empty space, return the set of constraints

    acting on that space. If there are no constraints, this is interpreted to
    mean a tile can't be played there. If this is the case or there is a tile in
    the space, return `None`.
    """
    if not board.can_place_tile_at(coord):
      return None

    directional_affixes = defaultdict(lambda: None)
    for direction in Direction:
      affix = ""
      curr_coord = coord.move(direction)
      while board.has_tile_at(curr_coord):
        affix += board[curr_coord]
        curr_coord = curr_coord.move(direction)

      if direction in [Direction.LEFT, Direction.UP]:
        # The affix must be in reading direction.
        affix = affix[::-1]

      if affix:
        directional_affixes[direction] = affix

    if not directional_affixes:
      return None

    return AffixConstraints.create_if_valid(
        dictionary,
        directional_affixes[Direction.LEFT],
        directional_affixes[Direction.RIGHT],
        directional_affixes[Direction.UP],
        directional_affixes[Direction.DOWN],
    )

  def check_constraints(
      self, letter: str, move_direction: Direction
  ) -> Tuple[bool, bool]:
    # A valid submove: all letter sequences formed are prefixes or suffixes of
    # known words.
    # A valid move: all letter sequences formed are words.
    if not self._directional_constraints:
      # Should only happen for single-letter words.
      return (True, letter in self._dictionary)

    (
        forms_horizontal_affixes,
        forms_horizontal_words,
    ) = self._check_constraint_for_reading_direction(letter, Direction.RIGHT)

    (
        forms_vertical_affixes,
        forms_vertical_words,
    ) = self._check_constraint_for_reading_direction(letter, Direction.DOWN)

    # A valid submove must have full words in the perpendicular directions.
    if move_direction.is_horizontal():
      is_valid_submove = forms_horizontal_affixes and forms_vertical_words
    else:
      is_valid_submove = forms_vertical_affixes and forms_horizontal_words

    is_valid_move = forms_vertical_words and forms_horizontal_words

    return (is_valid_submove, is_valid_move)

  def _check_constraint_for_reading_direction(
      self, letter: str, direction: Direction
  ) -> Tuple[bool, bool]:
    forms_valid_affixes = True
    forms_valid_words = True
    forward = direction
    backward = direction.inverse()

    # TODO: In this current implementation we assume that we are building the
    # word in one direction which is not true.

    if backward in self._directional_constraints:
      if forward in self._directional_constraints:
        prefix = self._directional_constraints[backward].affix
        suffix = self._directional_constraints[forward].affix
        forms_valid_words = (
            forms_valid_words and prefix + letter + suffix in self._dictionary
        )
        forms_valid_affixes = forms_valid_words
      else:
        constraint = self._directional_constraints[backward]
        forms_valid_words = (
            forms_valid_words and constraint.affix + letter in self._dictionary
        )
        forms_valid_affixes = forms_valid_affixes and letter in constraint.trie
    elif forward in self._directional_constraints:
      constraint = self._directional_constraints[forward]
      forms_valid_words = (
          forms_valid_words and letter + constraint.affix in self._dictionary
      )
      forms_valid_affixes = forms_valid_affixes and letter in constraint.trie

    return (forms_valid_affixes, forms_valid_words)

  def __repr__(self) -> str:
    return ", ".join(
        f"{d.name}: {obj.affix}"
        for d, obj in self._directional_constraints.items()
    )

  def update(
      self, point: Point, move_direction: Direction, context: ScrabbleContext
  ) -> AffixConstraints:
    directional_constraints = self._directional_constraints.copy()
    # Remove all perpendicular constraints; they no longer will apply.
    for direction in Direction:
      if direction not in (move_direction, move_direction.inverse()):
        directional_constraints.pop(direction, None)  # Remove if present.

    existing_constraints = context.solver_constraint_map[point]
    if existing_constraints:
      directional_constraints.update(
          existing_constraints._directional_constraints
      )

    return AffixConstraints(directional_constraints, context.dictionary)
