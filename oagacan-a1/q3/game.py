import sys, pygame
import solver16

pygame.init()

font = pygame.font.Font(None, 36)
size = width, height = 400, 400
screen = pygame.display.set_mode(size)
black = 0, 0, 0

# ball = pygame.image.load("ball.bmp")
# ballrect = ball.get_rect()

state = None

# while 1:
#    for event in pygame.event.get():
#        if event.type == pygame.QUIT: sys.exit()
#
#    ballrect = ballrect.move(speed)
#
#    if ballrect.left < 0 or ballrect.right > width:
#        speed[0] = -speed[0]
#    if ballrect.top < 0 or ballrect.bottom > height:
#        speed[1] = -speed[1]
#
#    screen.fill(black)
#    screen.blit(ball, ballrect)
#    pygame.display.flip()

def loop(state):
    current_row = 0
    current_col = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                # print "keydown", event.key
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)

                elif event.key == pygame.K_UP:
                    current_row = (current_row - 1) % state.size
                elif event.key == pygame.K_DOWN:
                    current_row = (current_row + 1) % state.size
                elif event.key == pygame.K_LEFT:
                    current_col = (current_col - 1) % state.size
                elif event.key == pygame.K_RIGHT:
                    current_col = (current_col + 1) % state.size

                move = None

                if event.key == pygame.K_w:
                    state = state.up(current_col)
                    move = "up(" + str(current_col) + ")"
                elif event.key == pygame.K_a:
                    state = state.left(current_row)
                    move = "left(" + str(current_row) + ")"
                elif event.key == pygame.K_s:
                    state = state.down(current_col)
                    move = "down(" + str(current_col) + ")"
                elif event.key == pygame.K_d:
                    state = state.right(current_row)
                    move = "right(" + str(current_row) + ")"

                if move:
                    print move, state.arr

        screen.fill(black)

        pygame.draw.rect(screen, (34, 83, 99),
                pygame.Rect(current_col * 100, current_row * 100, 100, 100))

        # print "current_row:", current_row, "current_col:", current_col

        for col in range(0, 4):
            for row in range(0, 4):
                x_start = col * 100 + 40
                y_start = row * 100 + 40
                num = state.num_at(col, row)
                text = font.render(str(num), 1, (255, 255, 255))
                screen.blit(text, (x_start, y_start))

        pygame.display.flip()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # leaky file descriptor
        state = solver16.parse_state(open(sys.argv[1], "r"))
    else:
        state = solver16.State(map(int, sys.argv[1:]))
    print "initial state:", state.arr
    loop(state)
