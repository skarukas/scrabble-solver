from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import math


@dataclass(eq=True, frozen=True)
class PlacedTile(object):
  letter: str
  location: Point


class Direction(Enum):
  UP = 0
  DOWN = 1
  LEFT = 2
  RIGHT = 3

  def inverse(self) -> Direction:
    if self == Direction.UP:
      return Direction.DOWN
    elif self == Direction.DOWN:
      return Direction.UP
    elif self == Direction.LEFT:
      return Direction.RIGHT
    else:
      return Direction.LEFT

  def is_horizontal(self) -> bool:
    return self in (Direction.LEFT, Direction.RIGHT)

  def is_vertical(self) -> bool:
    return not self.is_horizontal()


@dataclass(eq=True, frozen=True)
class Point:
  x: int
  y: int

  def move(self, direction: Direction) -> Point:
    if direction == Direction.UP:
      return Point(self.x, self.y - 1)
    elif direction == Direction.DOWN:
      return Point(self.x, self.y + 1)
    elif direction == Direction.LEFT:
      return Point(self.x - 1, self.y)
    else:
      return Point(self.x + 1, self.y)

  def distance(self, other: Point) -> float:
    return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

  def __str__(self) -> str:
    return f"({self.x}, {self.y})"
