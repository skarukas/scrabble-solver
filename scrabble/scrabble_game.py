from dataclasses import dataclass
from typing import Sequence

from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.scrabble_player import AbstractPlayer
from scrabble.context.tile_pool import TilePool
import scrabble.util.constants as C
from scrabble.util.constants import Style

@dataclass
class ScrabbleGame:
  context: ScrabbleContext
  players: Sequence[AbstractPlayer]
  tile_pool: TilePool
  _curr_player_idx: int = 0
  _game_over_override: bool = False

  def next_move(self):
    player = self.players[self._curr_player_idx]
    move = player.choose_next_move(self.context)
    if not move.placed_tiles:
      print("x", end="")
      player._rack_letters = self.tile_pool.draw(C.TILES_DRAWN_PER_PLAYER)
      #self._game_over_override = True
      self._next_player()
      return
    
    score = self.context.score_move(move, check_valid=True)
    player.total_score += score["total_score"]
    self.context = self.context.execute_move(move)
    self._next_player()
    
    print(f"{Style.FAIL(player.name)} has tiles {player._rack_letters} and just made this move:")
    print(self.context.board.printable_board(move.placed_tiles))
    score = score["total_score"]
    print(f"({score} points)")
    
    print(f"They now have {player.total_score} points!")

    player.play_tiles_and_draw(move, self.tile_pool)
  
  def _next_player(self):
    self._curr_player_idx = (self._curr_player_idx + 1) % len(self.players)

  def is_over(self) -> bool:
    return self._game_over_override or self.tile_pool.is_empty()

  def play(self):
    while not self.is_over():
      self.next_move()
    print(Style.BOLD("Final scores:"))
    for player in self.players:
      print(f"  {player.name}: {player.total_score} points")