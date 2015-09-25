import pygame
import sys
import time

import rameses

BLACK = 0, 0, 0
WHITE = 255, 255, 255

def mouse_grid_xy(cell_size):
    (mouse_x, mouse_y) = pygame.mouse.get_pos()
    return (mouse_x - (mouse_x % cell_size), mouse_y - (mouse_y % cell_size))

def mouse_grid(cell_size):
    (mouse_x, mouse_y) = pygame.mouse.get_pos()
    return (int(mouse_x / cell_size), int(mouse_y / cell_size))

def run_game(state, turn):
    import math

    pygame.init()
    font = pygame.font.Font(None, 36)
    font_x_size = font.size('x')
    font_dot_size = font.size('.')

    # By default list_modes returns fullscreen modes, and as far as I can see
    # output is ordered, i.e. first element is fullscreen resolution.
    (max_width, max_height) = pygame.display.list_modes()[0]

    # We always run in a square
    max_size = min(max_width, max_height)

    # No need to make cells huge
    size = max_size
    if max_size > 50 * state.size:
        size = 50 * state.size

    # Leave some room for window frame etc.
    if size >= max_size - 30:
        size = max_size - 30

    screen = pygame.display.set_mode((size, size))

    cell_size = float(size) / float(state.size)

    print "cell_size:", cell_size

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and turn:
                (col, row) = mouse_grid(cell_size)
                print "moving to", col, row
                state = state.move(col, row)

        screen.fill(BLACK)

        # draw columns
        for x in xrange(1, state.size):
            x_coord = x * cell_size
            pygame.draw.line(screen, WHITE, (x_coord, 0), (x_coord, size))

        # draw rows
        for y in xrange(1, state.size):
            y_coord = y * cell_size
            pygame.draw.line(screen, WHITE, (0, y_coord), (size, y_coord))

        # highlight cell under cursor
        (h_x, h_y) = mouse_grid_xy(cell_size)
        # print h_x, h_y
        pygame.draw.rect(screen, (34, 83, 99),
                pygame.Rect(h_x + 1, h_y + 1, cell_size - 2, cell_size - 2))

        # draw Xs
        for x in xrange(0, state.size):
            for y in xrange(0, state.size):
                c = state.at_xy(x, y)
                text = font.render(c, 1, (255, 255, 255))
                c_size = font_x_size
                if c == '.':
                    c_size = font_dot_size
                screen.blit(text, (x * cell_size + (cell_size - c_size[0]) / 2,
                                   y * cell_size + (cell_size - c_size[1]) / 2))

        pygame.display.flip()
        time.sleep(0.01)

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser("game.py")
    arg_parser.add_argument("board-size", type=int, nargs=1)
    arg_parser.add_argument("-fc", "--first-computer", action="store_true", default=False)

    args = vars(arg_parser.parse_args())

    state = rameses.Grid.empty(args["board-size"][0])
    # WOW!! This is ridiculous. Above I add the argument as "first-computer"
    # (note the hyphen, it's not underscore) but to read from the dictionary I
    # have to use underscore. This sucks! You're fired, Python!
    turn = args["first_computer"]

    # print state, turn

    run_game(state, turn)
