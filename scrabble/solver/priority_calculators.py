"""Priority calculations when executing graph search for Scrabble.

The priority calculation determines which states might be most promising to
explore first. A higher priority state will be explored first.
"""

from __future__ import annotations
from dataclasses import dataclass
from scrabble.solver.state import TerminalState, State
from scrabble.context.scrabble_context import ScrabbleContext


class PriorityCalculator:

  def calculate_priority(self, state: State) -> float:
    raise NotImplementedError()

  @staticmethod
  def create_from_option(
      option: str, context: ScrabbleContext
  ) -> PriorityCalculator:
    option = option.lower()
    if option == "total_score":
      return TotalScore(context)
    elif option == "uniform":
      return Uniform()


class Uniform(PriorityCalculator):

  def calculate_priority(self, state: State) -> float:
    return 1.0


@dataclass
class TotalScore(PriorityCalculator):
  _context: ScrabbleContext

  def calculate_priority(self, state: State) -> float:
    score_so_far = self._context.score_move(state.move, check_valid=False)
    return score_so_far["total_score"]
