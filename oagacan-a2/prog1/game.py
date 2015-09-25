import sys
import time

import rameses

BLACK = 0, 0, 0
WHITE = 255, 255, 255

def run_game(grid, turn):
    import pygame
    import math

    pygame.init()
    font = pygame.font.Font(None, 36)

    # By default list_modes returns fullscreen modes, and as far as I can see
    # output is ordered, i.e. first element is fullscreen resolution.
    (max_width, max_height) = pygame.display.list_modes()[0]

    # We always run in a square
    max_size = min(max_width, max_height)

    # No need to make cells huge
    size = max_size
    if max_size > 50 * grid.size:
        size = 50 * grid.size

    # Leave some room for window frame etc.
    if size >= max_size - 30:
        size = max_size - 30

    screen = pygame.display.set_mode((size, size))

    cell_size = float(size) / float(grid.size)

    print "cell_size:", cell_size

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        screen.fill(BLACK)

        # draw columns
        for x in xrange(1, grid.size):
            x_coord = x * cell_size
            pygame.draw.line(screen, WHITE, (x_coord, 0), (x_coord, size))

        # draw rows
        for y in xrange(1, grid.size):
            y_coord = y * cell_size
            pygame.draw.line(screen, WHITE, (0, y_coord), (size, y_coord))

        # highlight cell under cursor
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        h_x = mouse_x - (mouse_x % cell_size)
        h_y = mouse_y - (mouse_y % cell_size)
        # print h_x, h_y
        pygame.draw.rect(screen, (34, 83, 99),
                pygame.Rect(h_x + 1, h_y + 1, cell_size - 2, cell_size - 2))

        pygame.display.flip()
        time.sleep(0.01)

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser("game.py")
    arg_parser.add_argument("board-size", type=int, nargs=1)
    arg_parser.add_argument("-fc", "--first-computer", action="store_true", default=False)

    args = vars(arg_parser.parse_args())

    grid = rameses.Grid.empty(args["board-size"][0])
    # WOW!! This is ridiculous. Above I add the argument as "first-computer"
    # (note the hyphen, it's not underscore) but to read from the dictionary I
    # have to use underscore. This sucks! You're fired, Python!
    turn = args["first_computer"]

    # print grid, turn

    run_game(grid, turn)
