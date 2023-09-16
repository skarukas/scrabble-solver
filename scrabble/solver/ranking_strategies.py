"""Ranking strategies for Scrabble.

A ranking strategy determines which terminal state (potential move) will be
chosen as the best one.
"""

from __future__ import annotations

from dataclasses import dataclass
import random

from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.solver.state import TerminalState


class RankingStrategy:

  def is_better_than(self, state: TerminalState, other: TerminalState) -> bool:
    raise NotImplementedError()

  @staticmethod
  def create_from_option(option: str) -> RankingStrategy:
    option = option.lower()
    if option.startswith("random"):  # random:0.5
      p = 0.5 if option == "random" else float(option.split(":")[-1])
      return Random(p)
    elif option == "max_score":
      return MaxScore()
    elif option == "most_words":
      return MostWords()


@dataclass
class Random(RankingStrategy):
  p: float

  def is_better_than(self, state: TerminalState, other: TerminalState) -> bool:
    if state.score["total_score"] > other.score["total_score"]:
      prob = self.p
    else:
      prob = 1 - self.p

    return random.random() <= prob


class MaxScore(RankingStrategy):

  def is_better_than(self, state: TerminalState, other: TerminalState) -> bool:
    return state.score["total_score"] > other.score["total_score"]


class MostWords(RankingStrategy):

  def is_better_than(self, state: TerminalState, other: TerminalState) -> bool:
    return len(state.score["word_scores"]) > len(other.score["word_scores"])