from __future__ import annotations
import numpy as np
from typing import Tuple, Awaitable, Callable, List
from concurrent import futures
from queue import Queue
from dataclasses import dataclass
from enum import Enum

from scrabble_context import ScrabbleContext, Move, ScrabbleBoard, ScrabbleDictionary, PlacedTile
from scrabble_util import Point, Direction
import constants as C


Future = Awaitable
Score = int


class _ScrabbleWorkerPool(object):
    def __init__(self, context: ScrabbleContext):
        self._context = context
        #self._executor = futures.ProcessPoolExecutor(max_workers=C.MAX_NUM_WORKERS)
        self._executor = futures.ThreadPoolExecutor(
            max_workers=C.MAX_NUM_WORKERS)

    def shutdown(self):
        self._executor.shutdown()

    # Methods for spawning new workers.
    def best_row_move_async(self, row_idx: int) -> Future[Tuple[Score, Move]]:
        return self._executor.submit(self._best_row_move, row_idx)

    def best_column_move_async(self, col_idx: int) -> Future[Tuple[Score, Move]]:
        return self._executor.submit(self._best_column_move, col_idx)

    def _best_row_move(self, row_idx: int) -> Tuple[Score, Move]:
        """
        Find the most optimal move along row `row_idx`. Run by a separate worker.
        """
        best_move = row_idx
        best_score = row_idx

        print(
            f"Best result for row {row_idx}: {best_move} ({best_score} points)")
        return (best_score, best_move)

    def _best_column_move(self, col_idx: int) -> Tuple[Score, Move]:
        """
        Find the most optimal move along column `col_idx`. Run by a separate worker.
        """
        if col_idx == 0:
            best_move = Move([
                PlacedTile("N", 0, 0),
                PlacedTile("E", 0, 1),
                PlacedTile("E", 0, 2),
                PlacedTile("D", 0, 3),
                PlacedTile("L", 0, 4),
                PlacedTile("E", 0, 5),
                PlacedTile("S", 0, 6),
            ])
            best_score = self._context.score_move(best_move)["total_score"]
        else:
            best_score = 0
            best_move = None

        print(
            f"Best result for column {col_idx}: {best_move} ({best_score} points)")
        return (best_score, best_move)

    def _solve_prefix(self, prefix: str, coord: Point, direction: Direction) -> Tuple[Score, Move]:
        letters = self._context.player_letters
        subtree: ScrabbleDictionary.Trie = self._context.dictionary.get_subtree_with_prefix(
            prefix)
        q: Queue[_State] = Queue()

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


@dataclass
class _State:
    letters_left: List[str]
    move: Move
    point: Point
    subtrie: ScrabbleDictionary.Trie

    def update(self, placed_tile: PlacedTile, direction: Direction) -> _State:
        letters_left = self.letters_left.copy()
        letters_left.remove(placed_tile.letter)  # Remove first occurence.
        move = Move([*self.move.placed_tiles, placed_tile])
        subtrie = self.subtrie[placed_tile.letter]
        point = self.point.move(direction)
        return _State(letters_left, move, point, subtrie)

    def is_valid(self, context: ScrabbleContext) -> bool:
        return len(self.letters_left) > 0  \
          and self.point in context.board \
          and not context.board.has_tile_at(self.point)


class ScrabbleSolver(object):

    def __init__(self, context: ScrabbleContext):
        self.context = context

    def calculate_next_move(self) -> Move:
        """
        Calculate the optimal move M(B) by calculating the best move from all the rows and columns. The best move overall will be a sequence of tiles played across a row or column:
        ```
        M(B) = argmax{ argmax M(B[:, j]), argmax M(B[i, :]) }
        ```
        """
        worker_pool = _ScrabbleWorkerPool(self.context)
        async_subproblems = [
            *[worker_pool.best_row_move_async(j)
              for j in range(self.context.board.height)],
            *[worker_pool.best_column_move_async(i)
              for i in range(self.context.board.width)]]
        worker_pool.shutdown()

        get_score: Callable[[Tuple[Score, Move]], Score] = lambda tup: tup[0]
        best_score, best_move = max([sp.result()
                                     for sp in async_subproblems], key=get_score)
        return best_move


if __name__ == "__main__":
    context = ScrabbleContext("XXX", ScrabbleBoard(
        np.zeros((10, 10)).tolist()), [])
    solver = ScrabbleSolver(context)
    print(solver.calculate_next_move())
