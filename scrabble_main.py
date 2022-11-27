import numpy as np
from absl import app
from absl import flags
import scrabble_util as util
from scrabble_context import ScrabbleContext, ScrabbleBoard, Move, ScrabbleDictionary
from scrabble_solver import ScrabbleSolver, Score
from typing import Set
import constants as C


_DICTIONARY_FILEPATH = flags.DEFINE_string(
    "dict_filepath",
    C.DEFAULT_DICTIONARY_FILEPATH,
    "A path to a .txt file containing a word per line."
)

_BOARD_FILEPATH = flags.DEFINE_string(
    "board_filepath",
    C.DEFAULT_BOARD_FILEPATH,
    "A path to a .txt file containing the board as a grid."
)

_CURRENT_LETTERS = flags.DEFINE_string(
    "current_letters",
    None,
    "A string containing the letters that the player has, in any order and without spaces or punctuation. Blank tiles should be notated with an underscore. Example: --current_letters=EEFSC_"
)


def main(argv):
    board = ScrabbleBoard.open(_BOARD_FILEPATH.value)
    dictionary = ScrabbleDictionary.open(_DICTIONARY_FILEPATH.value)
    context = ScrabbleContext(_CURRENT_LETTERS.value, board, dictionary)
    solver = ScrabbleSolver(context)
    print("I'm thinking...")
    move: Move = solver.calculate_next_move()
    score_dict = context.score_move(move, check_valid=True)
    print("Here's the move you should do:")
    print(move)
    print("Score for this move:")
    print(score_dict)


if __name__ == "__main__":
    app.run(main)
