from __future__ import annotations
from typing import Sequence, List, Optional
from scrabble_dictionary import ScrabbleDictionary

from scrabble_util import PlacedTile, Point, Direction
import constants as C
from scrabble_move import Move, MoveType
from scrabble_board import ScrabbleBoard


class ScrabbleContext(object):
    """
    An object storing the global context of the Scrabble game.
    """

    def __init__(self, player_letters: str, board: ScrabbleBoard, dictionary: ScrabbleDictionary):
        self.player_letters = player_letters
        self.board = board
        self.dictionary = dictionary

    def score_move(self, move: Move, check_valid=False) -> int:
        """
        Calculate the score for the given move.
        """
        score_result = {}
        if move.is_bingo():
            score_result["bingo_bonus"] = C.BINGO_BONUS

        formed_words: Sequence[List[PlacedTile]] = self._get_words_formed_by_move(
            move)
        str_words = ["".join(tile.letter for tile in word)
                     for word in formed_words]
        word_scores = [self.board.score_single_word(
            word) for word in formed_words]
        if check_valid:
            for word in str_words:
                assert word in self.dictionary, f"{word} is not a valid Scrabble word."

        score_result["word_scores"] = list(zip(str_words, word_scores))
        score_result["total_score"] = sum(
            word_scores) + score_result.get("bingo_bonus", 0)

        return score_result

    def _get_words_formed_by_move(self, move: Move) -> Sequence[List[PlacedTile]]:
        if move.type == MoveType.EXCHANGE:
            return []

        new_board = self.board.execute_move(move)
        # print(new_board._array)
        # First find the word along the main direction, then find all words along the opposite direction.
        if move.type == MoveType.LEFT_RIGHT:
            words = [new_board.get_horizontal_word_at(move.placed_tiles[0].location)]
            for tile in move.placed_tiles:
                word = new_board.get_vertical_word_at(tile.location)
                if word is not None:
                    words.append(word)
            return words
        else:
            words = [new_board.get_vertical_word_at(move.placed_tiles[0].location)]
            for tile in move.placed_tiles:
                word = new_board.get_horizontal_word_at(tile.location)
                if word is not None:
                    words.append(word)
            return words
