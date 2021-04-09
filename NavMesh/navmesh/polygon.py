from abc import abstractmethod
from collections import MutableSequence, Sequence
from typing import List, overload

from shared.vector import Vec2


class Polygon(Sequence):

    def __init__(self, vertices: List[Vec2]):
        self.vertices = vertices

    @overload
    @abstractmethod
    def __getitem__(self, i: int) -> Vec2:
        return self.vertices[i]

    @overload
    @abstractmethod
    def __getitem__(self, s: slice) -> Sequence[Vec2]:
        return self.vertices[s]

    def __getitem__(self, i: int) -> Vec2:
        return self.vertices[i]

    def __len__(self) -> int:
        return len(self.vertices)



