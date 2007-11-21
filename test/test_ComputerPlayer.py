import sys, os
sys.path.append(os.getcwd())

from pytwixt import node_twixt as twixt
from index import render_game_board_image, ComputerPlayer

game = twixt.Twixt("muzi", "thanh", (10, 10))

c1 = ComputerPlayer("muzi")
c2 = ComputerPlayer("thanh")
players = {"muzi": c1, "thanh":c2}

turn_number = 0
game.current_player = game.player1
while True:

    xy = players[game.current_player].next_move(game)
    game.claim_node(xy, game.current_player)
    
    game.id = "test_cp_%i" % turn_number
    #render_game_board_image(game)
    turn_number += 1

    if game.has_won(game.current_player):
        #print "%s HAS WON THE GAME!\n" % game.current_player
        break
    else:
        game.current_player = game.opponent(game.current_player)
    



