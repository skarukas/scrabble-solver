
from typing import List, Optional
import copy

from scrabble_util import Direction, PlacedTile, Point
from scrabble_move import Move
from scrabble_board import ScrabbleBoard
import constants as C

class ScrabbleBoard(object):
    def __init__(self, array: List[List[str]]):
        self._array = array
        self.width = len(array[0])
        self.height = len(array)

    def __getitem__(self, *args):
        if len(args) == 1 and isinstance(args[0], Point):
          point = args[0]
          return self._array[point.x][point.y]
        return self._array.__getitem__(*args)

    def __contains__(self, point: Point) -> bool:
        return point.x in range(self.width) and point.y in range(self.height)
    
    def has_tile_at(self, point: Point) -> bool:
        c = self[point]
        return c.isalpha() or c == " "

    def score_single_word(self, tiles: List[PlacedTile]) -> int:
        """
        Calculate the score of a single "word" (tile sequence) when played on this board. Only points from the given tiles will contribute to the total.

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
            if self.has_tile_at(tile.point):
                raise RuntimeError(
                    f"Cannot place tile '{tile.letter}' at {tile.location} as '{self[tile.location]}' is already present.")
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

        while word_start in self and not self.has_tile_at(word_start.move(backward)):
            word_start = word_start.move(backward)

        while word_end in self and not self.has_tile_at(word_end):
            word_end.move(forward)
        
        if word_end.distance(word_start) <= 1:
            return None
        
        # Get all tiles from start to end.
        result = []
        pt = word_start
        while pt != word_end:
          tile = PlacedTile(self[pt], pt)
          result.append(tile)
          pt = word_start.move(forward)

        return result

    @staticmethod
    def open(fname: str) -> ScrabbleBoard:
        with open(fname) as file:
            board_array = [
                [square.strip() for square in line.split(" ") if square.strip() != ""] for line in file]
             
            return ScrabbleBoard(board_array)