from os import path
from pkg_resources import resource_filename

DOUBLE_WORD_SCORE = "w2"
TRIPLE_WORD_SCORE = "w3"
DOUBLE_LETTER_SCORE = "l2"
TRIPLE_LETTER_SCORE = "l3"

EMPTY_SQUARE = "-"
BLANK_TILE = "_"

TILES_DRAWN_PER_PLAYER = 7

TILE_SCORES = {
    "a": 1,
    "b": 3,
    "c": 3,
    "d": 2,
    "e": 1,
    "f": 4,
    "g": 2,
    "h": 4,
    "i": 1,
    "j": 8,
    "k": 5,
    "l": 1,
    "m": 3,
    "n": 1,
    "o": 1,
    "p": 3,
    "q": 10,
    "r": 1,
    "s": 1,
    "t": 1,
    "u": 1,
    "v": 4,
    "w": 4,
    "x": 8,
    "y": 4,
    "z": 10,
    BLANK_TILE: 10,
}

BINGO_BONUS = 50

MAX_NUM_WORKERS = 32

# Resources.
_PACKAGE_NAME = "scrabble"
RESOURCE_ROOT = resource_filename(_PACKAGE_NAME, "resources")
DEFAULT_DICTIONARY_FILEPATH = path.join(RESOURCE_ROOT, "word_list.txt")
DEFAULT_BOARD_FILEPATH = path.join(RESOURCE_ROOT, "board_1.txt")
