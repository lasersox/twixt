import os, cPickle, sys
import re
from pytwixt import node_twixt as twixt
import twixt_heuristic as heuristic
from bpnn import NN

class PlayerException(Exception):
  pass

class PlayerSecretException(Exception):
  pass

class PlayerExistsException(Exception):
  pass

class Player(object):
  
  def __eq__(self, other):
      if isinstance(other, Player):
          return self.name == other.name
      else:
          return self.name == other
          
  def __hash__(self):
      return hash(self.name)

  def save(self):
    f = open("state/player_%s.pickle" % re.escape(self.name), 'w')
    cPickle.dump(self, f)
    f.close()
    return self

  @staticmethod
  def load(name):
    fname = "state/player_%s.pickle" % re.escape(name)
    if os.path.exists(fname):
      f = open(fname)
      p = cPickle.load(f)
      return p
    else:
      raise PlayerExistsException("No such player exists.")

class HumanPlayer(Player):
  
  def __init__(self, name, secret):
    self.name   = name
    self.secret = sha.sha(secret).hexdigest()
  
  @staticmethod
  def login(name, secret):
    fname = "state/player_%s.pickle" % sha.sha(name).hexdigest()
    web.debug("Opening file %s..." % fname)
    if os.path.exists(fname):
      f = open(fname)
      p = cPickle.load(f)
      f.close()
      if p.secret == secret:
        return p
      else:
        raise PlayerSecretException("Invalid secret.")
    else:
      return HumanPlayer(name, secret).save()

class ComputerPlayer(object):
    
    def next_move(self, game):
        """ Just looking at one step ahead for now 
        1. Generate all possible game states
        2. Evaluate h = w1*f1 + w2*f2 + w3*f3...
        3. Pick the best one (greedy breadth first search) """
        
        game_states = heuristic.get_next_states(game,self.name,1)
        h = []
        
        for game_state in game_states[1]:
            h.append((self.get_score(game_state), game_state))
            
        next_node = max(h)[1][2]
        return (next_node.x, next_node.y)

    def next_minmax_move(self, game):
        """ Just looking at one step ahead for now 
        1. Generate all possible game states
        2. Evaluate h = w1*f1 + w2*f2 + w3*f3...
        3. Pick the best one (greedy breadth first search) """
        
        import copy
        #print "Getting next states..."
        game_states = heuristic.get_next_states(copy.deepcopy(game),self.depth)
        #print "Searching..."
        next_score, next_game = self.minimax_search(game_states, self.depth)
        #print next_score, next_game
        next_node = next_game[2]
        #print "Found %s." % str((next_node.x, next_node.y))
        return (next_node.x, next_node.y)
    
    def minimax_search(self, node, depth):
        
        #if this is a leaf node or having no children,
        # just simply return the score
        if node[1] == [] or depth == 0:
            #print self.get_score(node[0]), node
            game = node[0]
            score = self.get_score(node[0])
            game.id = "depth %s %r %r %s %f" % (depth, sorted(list(game.claimed_nodes())), node[2], self.name, score)
            #render_game_board_image(game)
            return score, node
        
        #Opponent's move, try to minimize the score because that 
        # is what the apponent wants to do
        if node[0].current_player != self.name:
            min_score = float(sys.maxint)
            min_node = []
            for child in node[1]:
                temp_score, temp_node = self.minimax_search(child, depth-1)
                if min_score > temp_score:
                   min_score, min_node = temp_score, child
            game = node[0]
            score = self.get_score(node[0])
            game.id = "depth %s %r %r %f" % (depth, sorted(list(game.claimed_nodes())), node[2], score)
            #render_game_board_image(game)
            return min_score, min_node
 
        # If this is our move, we would like to maximize our score
        if node[0].current_player == self.name:
            max_score = float(-sys.maxint)
            max_node = []
            for child in node[1]:
                temp_score, temp_node = self.minimax_search(child, depth-1)
                #print temp_score, temp_node
                if max_score < temp_score:
                    max_score = temp_score
                    max_node = child
            game = node[0]
            score = self.get_score(node[0])
            game.id = "depth %s %r %r %f" % (depth, sorted(list(game.claimed_nodes())), node[2], score)
            #render_game_board_image(game)
            return max_score, max_node

class PerceptronComputerPlayer(ComputerPlayer):
    
    def __init__(self, name, weights=None, search_depth=2, learning_rate=0.05):
        self.name = name
        self.learning_rate = learning_rate
        self.weights = [1./len(heuristic.fs)]*len(heuristic.fs) if not weights else weights
        self.depth = search_depth
    
    def get_score(self, game_state):
        import math
        perceptron = sum(self.weights[i]*f_i(game_state, self.name) for i, f_i in enumerate(heuristic.fs))
        log = file("score_log.txt", "a")
        p = math.tanh(0.25*perceptron)
        g = 0.5 * heuristic.g_1(game_state, self.name)
        log.write("p: %f, g: %f, p - g: %f\n" % (p, g, p - g))
        log.close()
        return p + g
    
    def update_weights(self, expected_score, actual_score, f_scores):
        """ Compare the difference between the predicted game state
        and the current game state and update the weights.
        The update formula is: 
        
        new_weight = current_weight + n*(desire_score - actual_score)*f_score
        """
        for i in range(len(self.weights)):
            self.weights[i] = self.weights[i] + self.learning_rate*(expected_score - actual_score)*f_scores[i]     
        return 0
        

class NeuralComputerPlayer(ComputerPlayer):
    
    def __init__(self, name, search_depth=2):
        self.name = name
        self.depth = search_depth
        self.net = NN(len(heuristic.fs) + len(heuristic.gs), 2, 1)
        self.inputs_buffer = []
        self.N = 0.05
        self.M = 0.01
    
    def get_score(self, game_state):
        import math
        effs = [f_i(game_state, self.name) for f_i in heuristic.fs]
        gees = [heuristic.g_1(game_state, self.name)]
        inputs = effs + gees
        self.inputs_buffer.append(inputs)
        output = self.net.score(inputs)
        return output
        return output + 1. * heuristic.g_0(game_state, self.name)
    
    def update_weights(self, expected_score, actual_score, f_scores):
        """ Compare the difference between the predicted game state
        and the current game state and update the weights.
        The update formula is: 
        
        new_weight = current_weight + n*(desire_score - actual_score)*f_score
        """
        self.net.update(self.inputs_buffer.pop(0))
        return self.net.backPropagate(actual_score, self.N, self.M)



class ThanhsComputerPlayer(ComputerPlayer):
  def next_move(self, game):
    (x,y) = (1,1)
    return (x,y)
      

class LanfrancosComputerPlayer(ComputerPlayer):
  pass

class AlexsComputerPlayer(ComputerPlayer):
    def __init__(self, name, weights=None, learning_rate=0):
            self.name = name
            self.heuristics = 8
            self.weights = [1./self.heuristics]*self.heuristics if not weights else weights
