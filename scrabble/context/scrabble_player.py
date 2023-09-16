from dataclasses import dataclass

from typing import List, Sequence

from scrabble.util.scrabble_move import Move
from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.tile_pool import TilePool
import scrabble.util.constants as C

class AbstractPlayer:
  name: str
  _rack_letters: List[str]
  total_score: int = 0

  def __init__(self, name: str, rack_letters: Sequence[str]):
    self.total_score = 0
    self._rack_letters = [l.lower() for l in rack_letters]
    self.name = name

  def choose_next_move(self, context: ScrabbleContext) -> Move:
    raise NotImplementedError()
  
  def play_tiles_and_draw(self, move: Move, tile_pool: TilePool) -> None:
    for tile in move.placed_tiles:
      self._rack_letters.remove(tile.letter)  # Remove first occurence.

    letters_needed = C.TILES_DRAWN_PER_PLAYER - len(self._rack_letters)
    self._rack_letters += tile_pool.draw(letters_needed)