from board import Board, Side, Position
from game import Game, Move


def test_game():
    game = Game(board=Board(9))
    board = game.board

    p1 = game.create_human_player(Side.Black)
    p2 = game.create_human_player(Side.White)

    game.register_action(Move(Side.Black, Position(1, 1)))
    game.register_action(Move(Side.White, Position(2, 1)))
    game.register_action(Move(Side.Black, Position(2, 2)))
    game.register_action(Move(Side.White, Position(1, 2)))
    game.register_action(Move(Side.Black, Position(1, 3)))
    game.register_action(Move(Side.White, Position(2, 3)))
    game.register_action(Move(Side.Black, Position(3, 1)))
    game.register_action(Move(Side.White, Position(3, 2)))

    board_should_be = """.OX......
O.O......
XO.......
.........
.........
.........
.........
.........
.........
"""

    assert str(board) == board_should_be
    assert game.white_score == 6.5
    assert game.black_score == 2


def quickmove(x: int, y: int, side: Side = [Side.White]) -> Move:
    if side[0] == Side.White:
        side[0] = Side.Black
    else:
        side[0] = Side.White
    return Move(side[0], Position(x, y))


def test_kill_surrounded():
    game = Game(board=Board(9))
    board = game.board

    p1 = game.create_human_player(Side.Black)
    p2 = game.create_human_player(Side.White)

    points = [
        (3, 3),
        (3, 4),
        (4, 4),
        (4, 5),
        (5, 5),
        (5, 6),
        (6, 6),
        (6, 7),
        (7, 7),
        (7, 8),
        (8, 8),
        (8, 9),
        (2, 4),
        (3, 5),
        (4, 6),
        (5, 7),
        (3, 6),
        (2, 5),
        (1, 5),
        (2, 6),
        (1, 6),
        (1, 4),
        (2, 7),
        (6, 8),
        (4, 7),
        (7, 9),
        (5, 8),
        (6, 9),
        (5, 9),
        (9, 9),
        (9, 8),
        (1, 3),
        (2, 3),
        (1, 2),
        (2, 2),
        (1, 1),
        (2, 1),
    ]

    for p in points:
        game.register_action(quickmove(*p))

    board_should_be = """.X.......
.X.......
.XX......
.X.X.....
X...X....
X.XX.X...
.X.X..X..
....X..XX
....X....
"""

    assert str(board) == board_should_be


def test_legal_suicidal_move():
    game = Game(board=Board(9))
    board = game.board

    p1 = game.create_human_player(Side.Black)
    p2 = game.create_human_player(Side.White)

    points = [
        (4, 2),
        (4, 3),
        (5, 3),
        (4, 4),
        (4, 5),
        (5, 4),
        (5, 5),
        (3, 3),
        (6, 4),
        (3, 4),
        (3, 2),
        (3, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (1, 5),
        (1, 4),
        (3, 6),
        (1, 6),
        (1, 3),
        (2, 5),
        (2, 7),
        (1, 8),
        (1, 7),
        (3, 7),
        (1, 5),
    ]

    board_should_be = """.........
..XX.....
XX..X....
.....X...
X..XX....
..X......
XXO......
O........
.........
"""

    for p in points:
        game.register_action(quickmove(*p))

    assert str(board) == board_should_be


def test_right_border_bug():
    game = Game(board=Board(9))
    board = game.board

    p1 = game.create_human_player(Side.Black)
    p2 = game.create_human_player(Side.White)

    game.register_action(Move(Side.Black, Position(9, 1)))
    game.register_action(Move(Side.White, Position(9, 2)))
    game.register_action(Move(Side.Black, Position(9, 3)))
    game.register_action(Move(Side.White, Position(9, 4)))
    game.register_action(Move(Side.Black, Position(8, 2)))

    board_should_be = """........X
.......X.
........X
........O
.........
.........
.........
.........
.........
"""

    assert str(board) == board_should_be
    assert game.white_score == 7.5
    assert game.black_score == 0
