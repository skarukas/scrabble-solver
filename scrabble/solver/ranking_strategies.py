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

  def pick_best(
      self, best_state: TerminalState, curr_state: TerminalState
  ) -> TerminalState:
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

  def pick_best(
      self, best_state: TerminalState, curr_state: TerminalState
  ) -> TerminalState:
    if curr_state.score["total_score"] > best_state.score["total_score"]:
      prob = self.p
    else:
      prob = 1 - self.p

    if random.random() <= prob:
      return curr_state
    else:
      return best_state


class MaxScore(RankingStrategy):

  def pick_best(
      self, best_state: TerminalState, curr_state: TerminalState
  ) -> TerminalState:
    if curr_state.score["total_score"] > best_state.score["total_score"]:
      s = curr_state.score["total_score"]
      print(f"New best: {curr_state.move} ({s} points)")
      return curr_state
    else:
      return best_state


class MostWords(RankingStrategy):

  def pick_best(
      self, best_state: TerminalState, curr_state: TerminalState
  ) -> TerminalState:
    if len(curr_state.score["word_scores"]) > len(
        best_state.score["word_scores"]
    ):
      return curr_state
    else:
      return best_state
