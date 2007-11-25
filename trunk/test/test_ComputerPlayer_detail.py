import sys, os

sys.path.append(os.chdir("../"))
sys.path.append(os.getcwd())


from pytwixt import node_twixt as twixt
from index import render_game_board_image, ComputerPlayer
import twixt_heuristic as heuristic
from random import random
import copy

def random_weights(N_heuristics):
    return [random() for i in range(N_heuristics)]
     

weights = random_weights(len(heuristic.fs))
#weights[6] = 1
#weights[5] = 1

game = twixt.Twixt("foo", "bar", (6, 6))
game.id = 0

game.claim_node((3,2), 'foo')
game.claim_node((2,1), 'bar')
#game.claim_node((2,2), 'foo')
#game.claim_node((2,3), 'bar')
#g.claim_node((4,1), 'foo')
render_game_board_image(game)
game.current_player = "foo"

c1 = ComputerPlayer("foo", copy.deepcopy(weights), search_depth = 2, learning_rate=0.09)
c2 = ComputerPlayer("bar", copy.deepcopy(weights), search_depth = 2, learning_rate=0.04)

print "Weights %s " % weights
    
players = {"bar": c2, "foo":c1}

turn_number = 0
#game.current_player = game.player1


#xy = players[game.current_player].next_minmax_move(game)
#print "Player %s claimed node %s." % (game.current_player, xy)
#game.claim_node(xy, game.current_player)
#game.id+=1
#render_game_board_image(game)
while True:

    xy = players[game.current_player].next_minmax_move(game)
    print "Player %s claimed node %s." % (game.current_player, xy)
    game.claim_node(xy, game.current_player)
    
    game.id = "test_cp_%02i" % turn_number
    #render_game_board_image(game)
    turn_number += 1
    render_game_board_image(game)
    if game.has_won(game.current_player):
        print "%s HAS WON THE GAME!\n" % game.current_player
        break
    else:
        game.current_player = game.opponent(game.current_player)


