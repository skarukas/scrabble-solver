from __future__ import annotations
import copy
from typing import List, Optional, Iterator, Sequence

from scrabble.util import constants as C
from scrabble.util.constants import Style
from scrabble.util.scrabble_move import Move
from scrabble.util.scrabble_util import Direction
from scrabble.util.scrabble_util import PlacedTile
from scrabble.util.scrabble_util import Point


class ScrabbleBoard:

  def __init__(self, array: List[List[str]]):
    self._array = array
    self.width = len(array[0])
    self.height = len(array)
    self._start_point = Point(self.width // 2, self.height // 2)

  def __getitem__(self, point: Point) -> str:
    if point not in self:
      raise IndexError(
          f"{point} is not in the board. WxH = {self.width}x{self.height}"
      )
    return self._array[point.x][point.y]

  def __contains__(self, point: Point) -> bool:
    return point.x in range(self.width) and point.y in range(self.height)

  def __iter__(self) -> Iterator[Point]:
    for x in range(self.width):
      for y in range(self.height):
        yield Point(x, y)

  def printable_board(self, highlighted_tiles: Optional[Sequence[PlacedTile]]=None) -> str:
    highlighted_tiles = set(tile.location for tile in highlighted_tiles) if highlighted_tiles else set()
    result = ""
    longdash = ("_" * 3 * self.width) + "\n"
    result += longdash
    for x in range(self.width):
      for y in range(self.height):
        point = Point(x, y)
        letter = self[point]
        is_highlighted = point in highlighted_tiles
        result += self._style_tile("{:3}".format(letter), is_highlighted)
      result += "\n"
    result += longdash
    return result.rstrip() 

  def __repr__(self) -> str:
    return self.printable_board()

  def _style_tile(self, c: str, is_highlighted=False) -> str:
    if c.strip().isalpha():
      if is_highlighted:
        styles = [Style.BOLD, Style.OKGREEN]
      else:
        styles = [Style.BOLD, Style.WARNING]
      return Style.apply_styles(c.upper(), *styles)
    else:
      return c

  def can_place_tile_at(self, point: Point) -> bool:
    return point in self and not self.has_tile_at(point)

  def has_tile_at(self, point: Point) -> bool:
    return point in self and (self[point].isalpha() or self[point] == " ")

  def point_touches_tiles(self, point: Point) -> bool:
    # TODO: rename.
    return point == self._start_point or any(
        self.has_tile_at(point.move(direction)) for direction in Direction
    )

  def score_single_word(self, tiles: List[PlacedTile]) -> int:
    """Calculate the score of a single "word" (tile sequence) when played on this board.

    Only points from the given tiles will contribute to the total.

    The only special tiles counted will be those that are exposed on the board.
    """
    raw_score = 0
    word_multiplier = 1
    for tile in tiles:
      board_tile = self[tile.location]
      letter_score = C.TILE_SCORES[tile.letter]
      if board_tile == C.DOUBLE_LETTER_SCORE:
        letter_score *= 2
      elif board_tile == C.TRIPLE_LETTER_SCORE:
        letter_score *= 3
      elif board_tile == C.DOUBLE_WORD_SCORE:
        word_multiplier *= 2
      elif board_tile == C.TRIPLE_WORD_SCORE:
        word_multiplier *= 3

      raw_score += letter_score

    return raw_score * word_multiplier

  def execute_move(self, move: Move) -> ScrabbleBoard:
    new_array = copy.deepcopy(self._array)
    for tile in move.placed_tiles:
      if not self.can_place_tile_at(tile.location):
        raise RuntimeError(
            f"Cannot place tile '{tile.letter}' at {tile.location} as"
            f" '{self[tile.location]}' is already present."
        )
      new_array[tile.location.x][tile.location.y] = tile.letter

    return ScrabbleBoard(new_array)

  def get_horizontal_word_at(self, start: Point) -> Optional[List[PlacedTile]]:
    return self._get_word_in_direction(start, Direction.RIGHT)

  def get_vertical_word_at(self, start: Point) -> Optional[List[PlacedTile]]:
    return self._get_word_in_direction(start, Direction.DOWN)

  def _get_word_in_direction(self, start: Point, reading_direction: Direction):
    forward = reading_direction
    backward = forward.inverse()
    word_start: Point = start
    word_end = word_start.move(forward)

    while self.has_tile_at(word_start.move(backward)):
      word_start = word_start.move(backward)

    while self.has_tile_at(word_end):
      word_end = word_end.move(forward)

    if word_end.distance(word_start) <= 1:
      return None

    # Get all tiles from start to end.
    result = []
    pt = word_start
    while pt != word_end:
      tile = PlacedTile(self[pt], pt)
      result.append(tile)
      pt = pt.move(forward)

    return result

  @staticmethod
  def open(fname: str) -> ScrabbleBoard:
    with open(fname) as file:
      board_array = [
          [
              square.strip().lower()
              for square in line.split(" ")
              if square.strip() != ""
          ]
          for line in file
      ]

      transpose = _transpose_array(board_array)

      return ScrabbleBoard(transpose)

def _transpose_array(a):
  transpose = [[None] * len(a) for _ in a[0]]
  for i in range(len(a)):
    for j in range(len(a[0])):
      transpose[j][i] = a[i][j]
  return a
