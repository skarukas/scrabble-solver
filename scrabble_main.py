from absl import app
from absl import flags
from scrabble.context.scrabble_board import ScrabbleBoard
from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.scrabble_dictionary import ScrabbleDictionary
from scrabble.solver.scrabble_solver import ScrabbleSolver
from scrabble.util import constants as C
from scrabble.util.scrabble_move import Move


_DICTIONARY_FILEPATH = flags.DEFINE_string(
    "dict_filepath",
    C.DEFAULT_DICTIONARY_FILEPATH,
    "A path to a .txt file containing a word per line.",
)

_BOARD_FILEPATH = flags.DEFINE_string(
    "board_filepath",
    C.DEFAULT_BOARD_FILEPATH,
    "A path to a .txt file containing the board as a grid.",
)

_CURRENT_LETTERS = flags.DEFINE_string(
    "current_letters",
    "chovies",
    (
        "A string containing the letters that the player has, in any order and"
        " without spaces or punctuation. Blank tiles should be notated with an"
        " underscore. Example: --current_letters=EEFSC_"
    ),
)

_PRUNING_STRATEGY = flags.DEFINE_string(
    "pruning_strategy",
    "never",  # "greedy_heuristic",
    "How to choose when to prune a state.",
)

_RANKING_STRATEGY = flags.DEFINE_string(
    "ranking_strategy", "max_score", "How to choose the best state."
)

_PRIORITY_CALCULATION = flags.DEFINE_string(
    "priority_calculation",
    "total_score",
    "How to choose which states to explore first.",
)


def main(argv):
  del argv
  board = ScrabbleBoard.open(_BOARD_FILEPATH.value)
  dictionary = ScrabbleDictionary.open(_DICTIONARY_FILEPATH.value)
  context = ScrabbleContext(_CURRENT_LETTERS.value, board, dictionary)
  solver = ScrabbleSolver.create_from_options(
      context,
      _PRIORITY_CALCULATION.value,
      _PRUNING_STRATEGY.value,
      _RANKING_STRATEGY.value,
  )
  print("I'm thinking...")
  move: Move = solver.calculate_next_move()
  score_dict = context.score_move(move, check_valid=True)
  print("Here's the move you should do:")
  print(move)
  print(board.execute_move(move))
  print("Score for this move:")
  print(score_dict)


if __name__ == "__main__":
  app.run(main)
