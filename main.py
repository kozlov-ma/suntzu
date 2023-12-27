import dataclasses
import enum
import itertools
import uuid
from abc import ABC
from dataclasses import dataclass
from functools import cache
from typing import Iterable

import pygame


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


@dataclass(frozen=True, repr=True)
class Action(ABC):
    side: Side


@dataclass(frozen=True, repr=True)
class Move(Action):
    pos: Position


@dataclass(frozen=True, repr=True)
class Pass(Action):
    pass


class IllegalMoveError(BaseException):
    pass


@dataclass(frozen=True)
class Player:
    game: "Game"
    id: uuid = dataclasses.field(default_factory=uuid.uuid4)


@dataclass
class Game:
    white_player: Player = None
    black_player: Player = None
    white_score: float = 0
    black_score: float = 6.5
    board: Board = dataclasses.field(default_factory=lambda: Board(19))
    log: list[Action] = dataclasses.field(default_factory=list)

    def create_human_player(self, preferred_side: Side | None = None):
        if (preferred_side is None or preferred_side == Side.Black) and self.black_player is None:
            p = Player(self)
            self.black_player = p
        elif (preferred_side is None or preferred_side == Side.White) and self.white_player is None:
            p = Player(self)
            self.white_player = p
        else:
            raise ValueError("Cannot create a new human player: desired player spots are already taken")
        return p

    def player_side(self, player: Player) -> Side:
        if player == self.white_player:
            return Side.White
        elif player == self.black_player:
            return Side.Black
        else:
            raise ValueError("Player was not in the game")

    def register_action(self, action: Action):
        # if not self.is_move_legal(action):
        #     raise IllegalMoveError('Tried to play an illegal move')

        self.log.append(action)
        match action:
            case Move(side, pos):
                self.board[pos] = side
            case Pass(side):
                pass

        self.kill_surrounded()

    def kill_surrounded(self):
        groups = {}
        for i in range(self.board.n):
            for j in range(self.board.n):
                if (i, j) in groups:
                    continue

                group = self.board.group_at(Position(i, j))
                groups |= dict.fromkeys(group, group)

        for group in groups.values():
            if not group:
                continue

            if self.board.is_surrounded(group):
                stone = self.board[next(iter(group))]
                if stone == Stone.White:
                    self.white_score += len(group)
                elif stone == Stone.Black:
                    self.black_score += len(group)
                self.board.delete_group(group)


WIDTH, HEIGHT = 900, 900
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


@cache
def init_graphics():
    pygame.font.init()
    background_image = pygame.image.load('background.jpeg')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.display.set_caption("suntzu -- Game of Go")
    screen.blit(background_image, (-320, -180))

    return screen, background_image


def draw_board(screen: pygame.Surface, bg_image: pygame.Surface, board: Board):
    interval = (WIDTH * 0.8) / (board.n - 1)
    verticals = [(WIDTH * 0.1) + i * interval for i in range(board.n)]
    horizontals = [(HEIGHT * 0.1) + i * interval for i in range(board.n)]

    screen.blit(bg_image, (-320, -180))
    for vertical in verticals:
        pygame.draw.line(screen, BLACK, (vertical, HEIGHT * 0.1), (vertical, HEIGHT * 0.9))

    for horizontal in horizontals:
        pygame.draw.line(screen, BLACK, (WIDTH * 0.1, horizontal), (WIDTH * 0.9, horizontal))

    for pos, stone in board:
        if stone is None:
            continue

        x = WIDTH * 0.1 + (pos.x - 1) * interval
        y = HEIGHT * 0.1 + (pos.y - 1) * interval

        color = BLACK if stone == Stone.Black else WHITE
        pygame.draw.circle(screen, color, (x, y), interval // 2)

    pygame.display.update()


def hot_seat():
    game = Game()
    board = game.board

    player1 = game.create_human_player(Side.Black)
    player2 = game.create_human_player(Side.White)

    players = itertools.cycle([player1, player2])

    screen, bg = init_graphics()

    draw_board(screen, bg, board)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                pygame.quit()
                return
            elif event.type == pygame.K_RETURN:
                player = next(players)
                act = Pass(game.player_side(player))
                game.register_action(act)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                player = next(players)
                y, x = pygame.mouse.get_pos()
                interval = (WIDTH * 0.8) / (board.n - 1)
                col = int(1 + (y - HEIGHT * 0.1 + 0.5 * interval) // interval)
                row = int(1 + (x - WIDTH * 0.1 + 0.5 * interval) // interval)

                act = Move(game.player_side(player), Position(col, row))
                try:
                    game.register_action(act)
                except Exception as e:
                    print(e)

                print('\n')
                print(board)
        draw_board(screen, bg, board)


if __name__ == "__main__":
    game_procedure = hot_seat
    game_procedure()
