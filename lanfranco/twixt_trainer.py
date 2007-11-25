
from random import random

# twixt_trainer.py

def random_weights(N_heuristics):
    return [random() for i in range(N_heuristics)]
        

def train(number_of_games=100, search_depth=2):
    
    assert search_depth % 2 == 0
    
    c1 = ComputerPlayer("muzi", random_weights(8), depth = 2)
    c2 = ComputerPlayer("thanh", random_weights(8), depth = 2)
    
    players = {"muzi": c1, "thanh":c2}
    
    """******** by Lan ********"""
    trainee_advantage = 0
    
    for n in range(number_of_games):
        score_buffer = []
        
        game = twixt.Twixt(p1.name, p2.name)
        game.id = str(n)
        
        trainee, teacher = p1, p2
        game.current_player = p1
        
        while True:
            
            if not heuristic.get_valid_nodes(game, game.current_player):
                break

            xy = players[game.current_player].next_move(game, search_depth)
            game.claim_node(xy, game.current_player)
            
            if trainee == game.current_player and len(score_buffer) == search_depth/2:
                expected_score = score_buffer.pop(0)
                actual_score = trainee.get_score(game)
                score_buffer.append(actual_score)
                trainee.update_weights(expected_score, actual_score)
                
            if game.has_won(game.current_player):
                
                """******** by Lan ********"""
                if game.current_player == trainee:
                    trainee_advantage += 1
                else:
                    traingee_advantage += -1
                """******** by Lan ********"""
                # print "%s HAS WON THE GAME!\n" % game.current_player
                break
            else:
                game.current_player = game.opponent(game.current_player)
        
        trainee, teacher = teacher, trainee
        del game
    
    
