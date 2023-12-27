import itertools
from functools import cache

import pygame

from board import Position, Side, Stone, Board
from game import Move, Pass, Game

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
            if event.type == pygame.QUIT or event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
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
