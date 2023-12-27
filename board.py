import dataclasses
import enum
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, unsafe_hash=True)
class Position:
    x: int
    y: int


class Side(enum.Enum):
    White = 'White'
    Black = 'Black'


Stone = Side


class PositionError(KeyError):
    pass


@dataclass
class Board:
    n: int = 19
    _stones: dict[Position, Side] = dataclasses.field(default_factory=dict)

    def __contains__(self, pos: Position) -> bool:
        return pos in self._stones

    def __getitem__(self, pos: Position) -> Side:
        return self._stones[pos]

    def __setitem__(self, pos: Position, side: Side):
        if not self.in_bounds(pos):
            raise PositionError('Position was out of bounds.')

        if pos in self._stones:
            raise PositionError('Tried to place stone on top of another stone')

        self._stones[pos] = side

    def neighbours_for(self, pos: Position) -> Iterable[Position]:
        for c in self.adjacent_positions(pos):
            if c in self:
                yield c

    def adjacent_positions(self, pos: Position) -> set[Position]:
        candidates = [Position(pos.x - 1, pos.y), Position(pos.x, pos.y + 1), Position(pos.x + 1, pos.y),
                      Position(pos.x, pos.y - 1)]
        return {c for c in candidates if self.in_bounds(c)}

    def group_at(self, pos: Position) -> set[Position]:
        if pos not in self:
            return set()

        q = [pos]
        visited = set()
        while q:
            v = q.pop()
            visited.add(v)
            for neighbour in (n for n in self.neighbours_for(v) if self[n] == self[pos]):
                if neighbour not in visited:
                    q.append(neighbour)
                    visited.add(neighbour)

        return visited

    def is_surrounded(self, group: Iterable[Position]) -> bool:
        for m in group:
            if len(set(self.neighbours_for(m))) < len(self.adjacent_positions(m)):
                return False

        return True

    def delete_group(self, group: Iterable[Position]):
        for member in group:
            self._stones.pop(member)

    def in_bounds(self, pos: Position) -> bool:
        return 1 <= pos.x <= self.n and 1 <= pos.y <= self.n

    def __iter__(self) -> Iterable[tuple[Position, Side | None]]:
        for x in range(self.n):
            for y in range(self.n):
                yield Position(x, y), self._stones.get(Position(x, y))

    def get(self, pos: Position) -> Side | None:
        if pos in self:
            return self[pos]
        else:
            return None

    def __str__(self):
        res = ""
        for i in range(self.n - 1, -1, -1):
            for j in range(self.n):
                side = self.get(Position(i, j))
                if side is None:
                    res += '.'
                elif side == Side.White:
                    res += 'O'
                elif side == Side.Black:
                    res += 'X'
            res += "\n"

        return res

    def __repr__(self):
        return str(self)
