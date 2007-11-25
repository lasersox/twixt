import sys, os

sys.path.append(os.chdir("../"))
sys.path.append(os.getcwd())


from pytwixt import node_twixt as twixt
from index import render_game_board_image, ComputerPlayer

weights = random_weights(len(heuristic.fs))
weights[8] = 1
weights[9] = 1

game = twixt.Twixt("muzi", "thanh", (5, 5))

c1 = ComputerPlayer("muzi", copy.deepcopy(weights), search_depth = 2, learning_rate=0.09)
c2 = ComputerPlayer("thanh", copy.deepcopy(weights), search_depth = 2, learning_rate=0.04)
    
players = {"muzi": c1, "thanh":c2}

turn_number = 0
game.current_player = game.player1
while True:

    xy = players[game.current_player].next_minmax_move(game)
    print "Player %s claimed node %s." % (game.current_player, xy)
    game.claim_node(xy, game.current_player)
    
    game.id = "test_cp_%i" % turn_number
    #render_game_board_image(game)
    turn_number += 1

    if game.has_won(game.current_player):
        print "%s HAS WON THE GAME!\n" % game.current_player
        break
    else:
        game.current_player = game.opponent(game.current_player)
    
    render_game_board_image(game)


