from typing import List, Dict
import random

Tile = str

class TilePool:
  def __init__(self, tile_counts: Dict[Tile, int], is_infinite=False):
    self._pool = []
    self._is_infinite = is_infinite
    for tile, count in tile_counts.items():
      self._pool += [tile] * count
  
  def is_empty(self) -> bool:
    return not self._pool

  def draw(self, num_tiles: int=1) -> List[Tile]:
    # Draw up to `num_tiles` tiles. May be less if empty.
    tiles = []
    for i in range(num_tiles):
      if self.is_empty():
        break
      tiles.append(self._draw_tile())
    return tiles
  
  def _draw_tile(self) -> Tile:
    idx = random.randint(0, len(self._pool)-1)
    tile = self._pool[idx]
    if not self._is_infinite:
      # Remove from the list in constant time.
      self._pool[idx], self._pool[-1] = self._pool[-1], self._pool[idx]
      self._pool.pop()
    return tile
