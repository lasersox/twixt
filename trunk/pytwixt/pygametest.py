## Testing Pygame ##
## By Teale Fristoe ##

import sys, pygame
from twixt import *
pygame.init()

# color definitions
black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
blue = 0, 0, 255
green = 0, 255, 0
orange = 200, 200, 100

# graphic size definitions
pegsize = 6
bridgewidth = 2
holesize = 4
selectsize = 8

# game definitions
p1 = Player('player 1', 'x', red)
p2 = Player('player 2', 'y', black)
game = Twixt(p2, p1, 10)
"""
peg1 = Peg((0,1))
peg2 = Peg((1,3))
bridge1 = Bridge((peg1, peg2))
peg3 = Peg((3,0))
game.insert_peg(peg1, p1)
game.insert_peg(peg2, p1)
game.insert_bridge(bridge1, p1)
game.insert_peg(peg3, p2)
"""

def convert(x):
    return 31 * x + 16
def unconvert(x):
    return x / 31

def displayplayer(screen, player):
    for peg in player.pegs:
        pygame.draw.circle(screen, player.color, map(convert,peg), pegsize)
    for bridge in player.bridges:
        pygame.draw.line(screen, player.color, map(convert,bridge.p1), map(convert,bridge.p2),bridgewidth)

def displaygame(screen, game):
    for x in range(game.size+2):
        for y in range(game.size+2):
            if not(x == 0 and y == 0) and not(x == 0 and y == game.size+1) and not(x == game.size+1 and y == 0) and not(x == game.size+1 and y == game.size+1):
                    pygame.draw.circle(screen, black, (convert(x), convert(y)), holesize)
    displayplayer(screen,game.player1)
    displayplayer(screen,game.player2)

size = width, height = (game.size + 2) * 31, (game.size + 2) * 31

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

play = True
down = False
selected = None

while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
            break
        screen.fill(white)
        mouse = map(unconvert, pygame.mouse.get_pos())
        if not(mouse[0] == 0 and mouse[1] == 0) and not(mouse[0] == 0 and mouse[1] == game.size+1) and not(mouse[0] == game.size+1 and mouse[1] == 0) and not(mouse[0] == game.size+1 and mouse[1] == game.size+1):
            pygame.draw.circle(screen, green, map(convert, mouse), selectsize)
            button = pygame.mouse.get_pressed()
            if button[0] and not(down):
                clicked = mouse
                down = True
            if not(button[0]) and down:
                if game.phase == 0:
                    if selected:
                        if mouse == clicked:
                            if mouse == selected:
                                selected = None
                            else:
                                if game.remove_bridge(Bridge((Peg(clicked), Peg(selected)))):
                                    pass
                                else:
                                    game.insert_bridge(Bridge((Peg(clicked), Peg(selected))))
                    else:
                        if game.insert_peg(Peg(mouse)):
                            selected = mouse
                            game.next_phase()
                        elif Peg(mouse) in game.curplayer.pegs:
                            selected = mouse
                elif game.phase == 1:
                    if mouse == clicked:
                        if mouse == selected:
                            selected = None
                            game.next_phase()
                        else:
                            game.insert_bridge(Bridge((Peg(clicked), Peg(selected))))
                down = False
                clicked = None
        if selected:
            pygame.draw.circle(screen, orange, map(convert, selected), selectsize)
        displaygame(screen, game)
        pygame.display.flip()
    clock.tick(60)
"""
                        if game.phase == 0:
                        if game.insert_peg(Peg(mouse)):
                            game.next_phase()
                        elif mouse in game.curplayer.pegs:
                            selected = None
                    elif game.phase == 1:
                        game.next_phase()
                else:
                    if game.phase == 0:
                        selected = None
                    elif game.phase == 1:
                        game.insert_bridge(Bridge(mouse, selected))
"""
