import itertools
from functools import cache

import pygame
import pygame_widgets as pw
from pygame_widgets.button import Button

from board import Position, Side, Stone, Board
from game import Move, Pass, Game

WIDTH, HEIGHT = 900, 900
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


@cache
def init_graphics(w=WIDTH, h=HEIGHT):
    pygame.init()
    pygame.font.init()
    background_image = pygame.image.load('background.jpeg')
    screen = pygame.display.set_mode((w, h))

    pygame.display.set_caption("suntzu -- Game of Go")
    screen.blit(background_image, (0, 0))

    return screen, background_image


def draw_board(screen: pygame.Surface, bg_image: pygame.Surface, board: Board):
    interval = (WIDTH * 0.8) / (board.n - 1)
    verticals = [(WIDTH * 0.1) + i * interval for i in range(board.n)]
    horizontals = [(HEIGHT * 0.1) + i * interval for i in range(board.n)]

    screen.blit(bg_image, (0, 0))
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


def get_n() -> int:
    screen, _ = init_graphics(750, 350)
    buttons = [pw.button.Button(screen, 100, 100, 150, 150, text='9x9', fontSize=50, margin=20, inactiveColour=WHITE,
        pressedColour=(0, 255, 0), radius=20),
        pw.button.Button(screen, 300, 100, 150, 150, text='13x13', fontSize=50, margin=20, inactiveColour=WHITE,
            pressedColour=(0, 255, 0), radius=20),
        pw.button.Button(screen, 500, 100, 150, 150, text='19x19', fontSize=50, margin=20, inactiveColour=WHITE,
            pressedColour=(0, 255, 0), radius=20), ]

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if abs(x - 100) <= 150 and abs(y - 100) <= 150:
                    return 9
                elif abs(x - 300) <= 150 and abs(y - 300) <= 150:
                    return 13
                elif abs(x - 500) <= 150 and abs(y - 500) <= 150:
                    return 19
                break

        for b in buttons:
            b.listen(events)
            b.draw()
            pygame.display.update()


def hot_seat():
    n = get_n()

    game = Game(board=Board(n))
    board = game.board

    screen, bg = init_graphics()

    player1 = game.create_human_player(Side.Black)
    player2 = game.create_human_player(Side.White)

    players = itertools.cycle([player1, player2])

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
