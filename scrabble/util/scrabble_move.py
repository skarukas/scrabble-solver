from enum import Enum
from typing import List, Optional

from scrabble.util import constants as C
from scrabble.util.scrabble_util import PlacedTile


class MoveType(Enum):
  LEFT_RIGHT = 0
  UP_DOWN = 1
  SINGLETON = 2
  EXCHANGE = 3


class Move:

  def __init__(
      self,
      placed_tiles: List[PlacedTile] = None,
      move_type: Optional[MoveType] = None,
  ):
    self.placed_tiles = placed_tiles or []
    self.type = move_type

  def is_bingo(self) -> bool:
    return len(self.placed_tiles) == C.TILES_DRAWN_PER_PLAYER

  def __str__(self) -> str:
    return (
        "{"
        + ", ".join(
            f"{tile.location}: {tile.letter})" for tile in self.placed_tiles
        )
        + "}"
    )

  def __repr__(self) -> str:
    return self.__str__()

  def get_move_type(self) -> MoveType:
    if self.type is not None:
      return self.type

    if not self.placed_tiles:
      move_type = MoveType.EXCHANGE
    elif len(self.placed_tiles) == 1:
      move_type = MoveType.SINGLETON
    else:
      x_coords = set(tile.location.x for tile in self.placed_tiles)
      y_coords = set(tile.location.y for tile in self.placed_tiles)

      if len(x_coords) == 1:
        move_type = MoveType.UP_DOWN
      elif len(y_coords) == 1:
        move_type = MoveType.LEFT_RIGHT
      else:
        raise RuntimeError(
            "The move is invalid. Tiles must be placed in a straight line."
        )

    self.type = move_type
    return move_type
