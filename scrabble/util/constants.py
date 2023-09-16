from __future__ import annotations

from os import path
from typing import Sequence
from pkg_resources import resource_filename
from enum import Enum

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

TILE_COUNTS = {
  "a": 9,
  "b": 2,
  "c": 2,
  "d": 4,
  "e": 12,
  "f": 2,
  "g": 3,
  "h": 2,
  "i": 9,
  "j": 1,
  "k": 1,
  "l": 4,
  "m": 2,
  "n": 6,
  "o": 8,
  "p": 2,
  "q": 1,
  "r": 6,
  "s": 4,
  "t": 6,
  "u": 4,
  "v": 2,
  "w": 2,
  "x": 1,
  "y": 2,
  "z": 1,
  #BLANK_TILE: 2 // TODO: be able to handle blank tiles.
}

BINGO_BONUS = 50

MAX_NUM_WORKERS = 32

# Resources.
_PACKAGE_NAME = "scrabble"
RESOURCE_ROOT = resource_filename(_PACKAGE_NAME, "resources")
DEFAULT_DICTIONARY_FILEPATH = path.join(RESOURCE_ROOT, "word_list.txt")
DEFAULT_BOARD_FILEPATH = path.join(RESOURCE_ROOT, "board_1.txt")


class Style(Enum):
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  
  @staticmethod
  def apply_styles(s: str, *styles: Sequence[Style]) -> str:
    return f"{''.join(map(str, styles))}{s}{Style.ENDC}"

  def __str__(self) -> str:
    return self.value
  
  def __call__(self, arg: str) -> str:
    return Style.apply_styles(arg, self)