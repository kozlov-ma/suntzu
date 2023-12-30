import dataclasses
import uuid
from abc import ABC
from dataclasses import dataclass

from board import Position, Side, Board


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
    white_score: float = 6.5
    black_score: float = 0
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

        ws, bs = self.board.kill_surrounded()
        self.white_score += ws
        self.black_score += bs


