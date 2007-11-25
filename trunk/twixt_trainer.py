import sys

from pytwixt import node_twixt as twixt
import twixt_heuristic as heuristic
from twixt_player import PerceptronComputerPlayer
from index import render_game_board_image
from random import random
import copy

# twixt_trainer.py

def random_weights(N_heuristics):
    return [random() for i in range(N_heuristics)]
        

def train(number_of_games=100, search_depth=2):
    
    assert search_depth % 2 == 0
    weights = random_weights(len(heuristic.fs))
    # The following weights are tuned for (unscaled) 0.5 * g_1 plus output of perceptron with f_1, ..., f_5.
    #  weights = [0.80645065474968314, 0.73851632090876906, -0.018709876472095509, 0.067931480573086053, 0.341251139029706]
    #  weights = [0.78256345518575787, 0.72806061248232179, -0.047892301965649302, -0.0088772339336371277, 0.34506233417550852]
    #  weights = [0.77115418840969974, 0.71555104743300879, -0.00081140756190061988, -0.054876323944738327, 0.3665955789374965]
    #  weights = [0.74288563817636388, 0.70486729316165075, 0.052725832294392469, -0.098542258526105236, 0.44418131498229901]
    # print "Weights for the players: %s" % weights
    c1 = PerceptronComputerPlayer("muzi", weights, search_depth = 2, learning_rate=0.05)
    c2 = PerceptronComputerPlayer("thanh", copy.deepcopy(weights), search_depth = 2, learning_rate=0.04)
    
    players = {"muzi": c1, "thanh":c2}
    
    score_status = [0,0,0]
    
    for n in range(number_of_games):

        score_buffer = []
        
        game = twixt.Twixt(c1.name, c2.name, (6,6))
        game.id = str(n)
        
        game.claim_node((2,3), c1.name)
        
        trainee, teacher = c1, c2
        game.current_player = c2.name
        
        while True:
            
            if not heuristic.get_valid_nodes(game):
                # print "Nobody won..."
                score_status[2] += 1
                break
            ## print "asking %s for his move..." % game.current_player
            xy = players[game.current_player].next_minmax_move(game)
            try:
                game.claim_node(xy, game.current_player)
            except twixt.NodeError, e:
                # print "%s reserved for %s" % (xy, game.nodes[xy].reservee)
                raise e
            # print game.current_player + " claimed node %s." % str(xy)
            
            if trainee.name == game.current_player and len(score_buffer) == search_depth/2:
                # print "Updating trainee..."
                expected_score = score_buffer.pop(0)
                actual_score = trainee.get_score(game)
                score_buffer.append(actual_score)
                effs = [f_i(game, trainee.name) for f_i in heuristic.fs]
                #old_weights = copy.deepcopy(trainee.weights)
                error = trainee.update_weights(expected_score, actual_score, effs)
                print "error: %r" % error
                # print [old_weights[i] - trainee.weights[i] for i in range(len(trainee.weights))]
            elif trainee.name == game.current_player and len(score_buffer) != search_depth/2:
                actual_score = trainee.get_score(game)
                score_buffer.append(actual_score)
            
            if game.has_won(game.current_player):
                #print "%s HAS WON THE GAME!" % game.current_player
                if game.current_player == "muzi":
                    score_status[0] +=1
                else:
                    score_status[1] +=1        
                break
            else:
                game.current_player = game.opponent(game.current_player)
        
        render_game_board_image(game)
        print "Game %s finished: Game status [Muzi,Thanh,Draw] = %s" % (n,score_status)
        if n%5 == 0:
            print "Trained weights: %s" % c1.weights
        del game
    
    print "Trained weights: %s" % c1.weights
    c1.save()
    c2.save()

if __name__ == "__main__":
    train(number_of_games=100, search_depth=2)
