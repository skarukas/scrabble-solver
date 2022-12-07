from __future__ import annotations

from dataclasses import dataclass
import random

from scrabble.solver.state import TerminalState
from scrabble.solver.state import State


class PruningStrategy:

  def should_prune(self, best_state: TerminalState, curr_state: State) -> bool:
    raise NotImplementedError()

  @staticmethod
  def create_from_option(
      option: str, context: ScrabbleContext
  ) -> PruningStrategy:
    option = option.lower()
    if option == "never":
      return NeverPrune()
    elif option.startswith("random"):
      p = 0.5 if option == "random" else float(option.split(":")[-1])
      return Random(p)
    elif option == "greedy_heuristic":
      return GreedyHeuristic()


class NeverPrune(PruningStrategy):

  def should_prune(self, best_state: TerminalState, curr_state: State) -> bool:
    return False


@dataclass
class Random(PruningStrategy):
  p: float

  def should_prune(self, best_state: TerminalState, curr_state: State) -> bool:
    return random.random() < self.p


class GreedyHeuristic(PruningStrategy):
  # TODO: implement
  def should_prune(self, best_state: TerminalState, curr_state: State) -> bool:
    raise NotImplementedError()
