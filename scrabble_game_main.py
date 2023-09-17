from absl import app
from absl import flags
from scrabble.context.scrabble_board import ScrabbleBoard
from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.scrabble_dictionary import ScrabbleDictionary
from scrabble.context.tile_pool import TilePool
from scrabble.solver.scrabble_solver import ComputerPlayer
from scrabble.util import constants as C
from scrabble.util.scrabble_move import Move
from scrabble.scrabble_game import ScrabbleGame


_DICTIONARY_FILEPATH = flags.DEFINE_string(
    "dict_filepath",
    C.DEFAULT_DICTIONARY_FILEPATH,
    "A path to a .txt file containing a word per line.",
)

_BOARD_FILEPATH = flags.DEFINE_string(
    "board_filepath",
    C.DEFAULT_BOARD_FILEPATH,
    "A path to a .txt file containing the initial board as a grid.",
)

_CURRENT_LETTERS = flags.DEFINE_string(
    "current_letters",
    "heat",
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

_PRIORITY_CALCULATION = flags.DEFINE_enum(
    "priority_calculation",
    "total_score",
    ["total_score", "uniform"],
    "How to choose which states to explore first.",
)


def main(argv):
  del argv
  board = ScrabbleBoard.open(_BOARD_FILEPATH.value)
  dictionary = ScrabbleDictionary.open(_DICTIONARY_FILEPATH.value)
  context = ScrabbleContext(board, dictionary)
  pool = TilePool(C.TILE_COUNTS, is_infinite=False)
  players = [
    ComputerPlayer(f"bot1 (objective={_RANKING_STRATEGY.value})", pool.draw(C.TILES_DRAWN_PER_PLAYER), context, _PRIORITY_CALCULATION.value, _PRUNING_STRATEGY.value, _RANKING_STRATEGY.value),
    ComputerPlayer(f"bot2 (objective={_RANKING_STRATEGY.value})", pool.draw(C.TILES_DRAWN_PER_PLAYER), context, _PRIORITY_CALCULATION.value, _PRUNING_STRATEGY.value, _RANKING_STRATEGY.value)
  ]
  game = ScrabbleGame(context, players, pool)

  game.play()


if __name__ == "__main__":
  app.run(main)
