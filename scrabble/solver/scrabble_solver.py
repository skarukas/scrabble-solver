from __future__ import annotations

from collections import defaultdict
from concurrent import futures
from dataclasses import dataclass, field
import queue as Q
from typing import Awaitable, Callable, Optional, Sequence, Tuple, Any

from scrabble.solver import priority_calculators
from scrabble.solver import pruning_strategies
from scrabble.solver import ranking_strategies
from scrabble.solver.constraints import AffixConstraints
from scrabble.context.scrabble_context import Move
from scrabble.context.scrabble_context import MoveType
from scrabble.context.scrabble_context import ScrabbleBoard
from scrabble.context.scrabble_context import ScrabbleContext
from scrabble.context.scrabble_context import ScrabbleDictionary
from scrabble.solver.state import State
from scrabble.solver.state import TerminalState
from scrabble.util import constants as C
from scrabble.util.scrabble_util import Direction
from scrabble.util.scrabble_util import Point


Future = Awaitable
Score = dict


@dataclass(order=True)
class _QueueItem:
  priority: int
  state: Any = field(compare=False)


class _ScrabbleWorkerPool(object):

  def __init__(self, context: ScrabbleContext):
    self._context = context
    self._executor = futures.ThreadPoolExecutor(max_workers=C.MAX_NUM_WORKERS)

  def shutdown(self):
    self._executor.shutdown()

  # Methods for spawning new workers.
  def best_row_move_async(self, row_idx: int) -> Future[Tuple[Score, Move]]:
    return self._executor.submit(self._best_row_move, row_idx)

  def best_column_move_async(self, col_idx: int) -> Future[Tuple[Score, Move]]:
    return self._executor.submit(self._best_column_move, col_idx)

  def _best_row_move(self, row_idx: int) -> Tuple[Score, Move]:
    """Find the most optimal move along row `row_idx`.

    Run by a separate worker.
    """
    raise NotImplementedError()

  def _best_column_move(self, col_idx: int) -> Tuple[Score, Move]:
    """Find the most optimal move along column `col_idx`.

    Run by a separate worker.
    """
    raise NotImplementedError()

  def _solve_prefix(
      self, prefix: str, coord: Point, direction: Direction
  ) -> Tuple[Score, Move]:
    letters = self._context.player_letters
    subtree: ScrabbleDictionary.Trie = (
        self._context.dictionary.get_subtree_with_prefix(prefix)
    )
    q: Queue[State] = Queue()

    best_score = 0
    best_move = None
    # state = (move, letters_left, curr_coord, subtrie)
    while q:
      state = q.get()
      move, letters_left, curr_coord, subtrie = state

      # todo: check coords and make sure we don't collide with word after
      for letter in set(letters_left):
        # If this condition is True, words with prefix `prefix+letter` exist.
        if letter in subtrie:
          new_state = state.update_state(direction)
          if new_state.is_valid(self._context):
            q.put(new_state)

      if ScrabbleDictionary.END_TOKEN in subtrie:
        curr_score = self._context.score_move(move)["total_score"]
        if curr_score > best_score:
          best_score = curr_score
          best_move = move

    return (best_score, best_move)


class ScrabbleSolver:

  def __init__(
      self,
      context: ScrabbleContext,
      priority: priority_calculators.PriorityCalculator,
      pruner: pruning_strategies.PruningStrategy,
      ranker: ranking_strategies.RankingStrategy,
  ):
    self._priority = priority
    self._pruner = pruner
    self._ranker = ranker
    self._context = context

  @staticmethod
  def create_from_options(
      context: ScrabbleContext,
      priority_strategy: str,
      pruner_strategy: str,
      ranker_strategy: str,
  ):
    return ScrabbleSolver(
        context,
        priority_calculators.PriorityCalculator.create_from_option(
            priority_strategy, context
        ),
        pruning_strategies.PruningStrategy.create_from_option(
            pruner_strategy, context
        ),
        ranking_strategies.RankingStrategy.create_from_option(ranker_strategy),
    )

  def calculate_next_move(self) -> Move:
    return self._calculate_next_move_graph()

  def _get_start_states_old(self) -> Sequence[State]:
    start_states = []
    constraint_map = defaultdict(lambda: None)
    for coord in self._context.board:
      constraints = AffixConstraints.get_constraints_at_point(
          self._context.board, self._context.dictionary, coord
      )
      if constraints is not None:
        constraint_map[coord] = constraints
        state = State(
            self._context.player_letters,
            Move([]),
            coord,
            constraints,
            direction=None,
        )
        start_states.append(state)
    # Needed during state updating in graph search.
    self._context.solver_constraint_map = constraint_map

    # TODO: Add special case for when the board is empty / first move.
    print("Start points:")
    print([state.point for state in start_states])
    return start_states

  def _get_start_states(self) -> Sequence[State]:
    start_states = []
    for coord in self._context.board:
      if self._context.board.can_place_tile_at(coord):
        constraints = AffixConstraints.get_constraints_at_point(
            self._context.board, self._context.dictionary, coord
        )
        constraints = constraints or AffixConstraints(
            {}, self._context.dictionary
        )
        state = State(
            self._context.player_letters,
            Move([]),
            coord,
            constraints,
            direction=None,
            touches_tile=self._context.board.point_touches_tiles(coord)
        )
        start_states.append(state)

    return start_states

  def _calculate_next_move_graph(self) -> Move:
    start_states = self._get_start_states()
    best_state = self._graph_search(start_states)
    if best_state is None:
      # TODO: Figure out which letters to exchange.
      return Move([], MoveType.EXCHANGE)
    else:
      return best_state.move

  def _calculate_next_move_rowcol(self) -> Move:
    """Calculate the optimal move M(B) by calculating the best move from all the rows and columns.

    The best move overall will be a sequence of tiles played across a row or
    column: ``` M(B) = argmax{ argmax M(B[:, j]), argmax M(B[i, :]) } ```
    """
    worker_pool = _ScrabbleWorkerPool(self.context)
    async_subproblems = [
        *[
            worker_pool.best_row_move_async(j)
            for j in range(self.context.board.height)
        ],
        *[
            worker_pool.best_column_move_async(i)
            for i in range(self.context.board.width)
        ],
    ]
    worker_pool.shutdown()

    get_score: Callable[[Tuple[Score, Move]], Score] = lambda tup: tup[0]
    best_score, best_move = max(
        [sp.result() for sp in async_subproblems], key=get_score
    )
    return best_move

  def _graph_search(
      self, start_states: Sequence[State]
  ) -> Optional[TerminalState]:
    """Execute a graph search from a set of given states.

    Args:
      start_states: The initial states to start from.

    Returns:
      The best terminal state according to the ranker. This returns None if
      no terminal states are found.
    """
    queue: Q.PriorityQueue[Tuple[float, State]] = Q.PriorityQueue()

    for start_state in start_states:
      item = _QueueItem(
          -self._priority.calculate_priority(start_state), start_state
      )
      queue.put(item)

    best_candidate: Optional[TerminalState] = None
    while not queue.empty():
      state = queue.get().state
      terminal_candidates, child_states = state.get_child_states(self._context)
      for child_state in child_states:
        if not self._pruner.should_prune(best_candidate, child_state):
          item = _QueueItem(
              -self._priority.calculate_priority(child_state), child_state
          )
          queue.put(item)

      for candidate in terminal_candidates:
        # print("Terminal:")
        # print(candidate.move.placed_tiles)
        if best_candidate is None:
          best_candidate = candidate
        else:
          best_candidate = self._ranker.pick_best(best_candidate, candidate)

    return best_candidate


if __name__ == "__main__":
  _context = ScrabbleContext(
      "XXX", ScrabbleBoard(np.zeros((10, 10)).tolist()), []
  )
  solver = ScrabbleSolver(_context)
  print(solver.calculate_next_move())
