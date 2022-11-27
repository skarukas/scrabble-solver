from enum import Enum
from typing import List, Optional

from scrabble_util import PlacedTile
import constants as C


class MoveType(Enum):
    LEFT_RIGHT = 0
    UP_DOWN = 1
    SINGLETON = 2
    EXCHANGE = 3


class Move(object):

    def __init__(self, placed_tiles: List[PlacedTile], move_type: Optional[MoveType]=None):
        self.placed_tiles = placed_tiles
        self.type = Move._get_move_type(placed_tiles) if move_type is None else move_type

    def is_bingo(self) -> bool:
        return len(self.placed_tiles) == C.TILES_DRAWN_PER_PLAYER

    def __str__(self) -> str:
        return ", ".join(f"{tile.location}: {tile.letter}" for tile in self.placed_tiles)

    @staticmethod
    def _get_move_type(tiles) -> MoveType:
        if len(tiles) == 0:
            return MoveType.EXCHANGE
        if len(tiles) == 1:
            return MoveType.SINGLETON

        x_coords = set(tile.location.x for tile in tiles)
        y_coords = set(tile.location.y for tile in tiles)

        if len(x_coords) == 1:
            return MoveType.UP_DOWN
        elif len(y_coords) == 1:
            return MoveType.LEFT_RIGHT
        else:
            raise RuntimeError(
                "The move is invalid. Tiles must be placed in a straight line.")
