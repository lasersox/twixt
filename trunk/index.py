# coding: utf-8

import os, cPickle, sys
import re
import sha
import web
from pytwixt import node_twixt as twixt
import twixt_heuristic as heuristic
from twixt_player import *

sys.stdout.sync = True
# console = open("/dev/console", "w")

render = web.template.render('templates/', cache=False)

urls = (
  '/play/',    'play',
  '/login/',   'login',
  '/new/',     'new_game',
  '/join/',    'join_game',
  '/waiting/', 'waiting',
  '/',         'index'
)

NODE_SPACING = 32
NODE_RADIUS = 4

def render_game_board_image(game):
  try:
    import Image, ImageDraw
  except ImportError:
    raise ImportError("Execution failed because the required “Python Imaging Library” is missing.\n"\
                     "Get it here: http://www.pythonware.com/products/pil/\n")
  
  player_color = {game.player1 : "#4444FF", game.player2: "#FF4444", "": "#aaaaaa"}
  
  m = NODE_SPACING
  r = NODE_RADIUS
  
  size = (game.size[0] + 1) * m, (game.size[1] + 1) * m
  im = Image.new("RGB", size)
  
  try:
    import aggdraw
    draw = aggdraw.Draw(im)
    p = aggdraw.Pen("black", 1)
    player_brush = {game.player1 : aggdraw.Brush(player_color[game.player1]),
                    game.player2 : aggdraw.Brush(player_color[game.player2]),
                    ""           : aggdraw.Brush(player_color[''])}
    player_pen = {game.player1 : aggdraw.Pen(player_color[game.player1], width=2),
                  game.player2 : aggdraw.Pen(player_color[game.player2], width=2),
                  ""           : aggdraw.Pen(player_color[''], width=2)}
    # print "Using aggdraw..."
  except ImportError:
    aggdraw = None
    draw = ImageDraw.Draw(im)
  
  left_top = lambda nd: (int(m*(nd.x+1) - r), int(m*(nd.y+1) + r))
  left_bot = lambda nd: (int(m*(nd.x+1) - r), int(m*(nd.y+1) - r))
  righ_top = lambda nd: (int(m*(nd.x+1) + r), int(m*(nd.y+1) + r))
  righ_bot = lambda nd: (int(m*(nd.x+1) + r), int(m*(nd.y+1) - r))
  
  center = lambda nd: (int(m*(nd.x+1)), int(m*(nd.y+1)))
  class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
  if aggdraw is not None:
    draw.rectangle([0, 0, size[0], size[1]], aggdraw.Brush("white"))
    draw.line(center(point(0,0.5))  + center(point(game.size[0]-1,0.5)),  player_pen[game.player2])
    draw.line(center(point(0,game.size[1]-1.5))   + center(point(game.size[0]-1,game.size[1] - 1.5)), player_pen[game.player2])
    draw.line(center(point(0.5,0))    + center(point(0.5,game.size[1]-1)),  player_pen[game.player1])
    draw.line(center(point(game.size[0]-1.5,0))   + center(point(game.size[0]-1.5,game.size[1]-1)), player_pen[game.player1])
  else:
    draw.rectangle([0, 0, size[0], size[1]], fill="#FFFFFF")
  
  for conn in game.connections():
      if aggdraw is not None:
          draw.line(center(conn.p0) + center(conn.p1), player_pen[conn.p0.owner])
      else:
          draw.line([center(conn.p0), center(conn.p1)], fill=player_color[conn.p0.owner], width=4)
  
  for node in game.nodes.values():
    # print "Drawing %s..." % node
    box = left_bot(node) + righ_top(node)
    if aggdraw is not None:
      draw.ellipse(box, p, player_brush[node.owner])
    else:
      draw.ellipse(box, fill=player_color[node.owner], outline="#000000")
  
  if aggdraw is not None:
    draw.flush()
  del draw
  im.save("./static/%s.png" % game.id)

def area_tags(game):
    m = NODE_SPACING
    tags = []
    t = "%i,%i,%i"
    for nd in game.nodes.values():
        tags.append((t % (int(m*(nd.x+1)), int(m*(nd.y+1)), NODE_RADIUS), "%i,%i" % (nd.x,nd.y)))
    return tags

def load_current_player():
  p = None
  c = web.cookies()
  if 'name' in c:
    p = HumanPlayer.load(c['name'])
  else:
    return None
  if p.secret == c['secret']:
    return p
  else:
    raise Exception("Bad secret.")

def GameError(Exception):
  pass

def load_game(game_id):
  f = open("state/game_%s" % game_id)
  g = cPickle.load(f)
  f.close()
  return g

def save_game(game):
  try:
    f = open("state/game_%s" % game.id, 'w')
    cPickle.dump(game, f)
    f.close()
  except:
    f.close()
  del f

def waiting_players():
  if os.path.exists('state/waiting_players'):
    f = open('state/waiting_players')
    games = cPickle.load(f)
    f.close()
  else:
    games = set([])
  return games

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
    f = open("state/player_%s" % re.escape(self.name), 'w')
    cPickle.dump(self, f)
    f.close()
    return self

  @staticmethod
  def load(name):
    fname = "state/player_%s" % re.escape(name)
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
    fname = "state/player_%s" % sha.sha(name).hexdigest()
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

class ComputerPlayer(Player):
    
    def __init__(self, name, weights=None, search_depth=2, learning_rate=0.05):
        self.name = name
        self.learning_rate = learning_rate
        self.weights = [1./len(heuristic.fs)]*len(heuristic.fs) if not weights else weights
        self.depth = search_depth
            
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
    
    def get_score(self, game_state):
        import math
        f = sum(self.weights[i]*f_i(game_state, self.name) for i, f_i in enumerate(heuristic.fs))
        n1 = math.tanh(0.5*f)
        return 1 * n1 #+ 0.5 * heuristic.g_1(game_state, self.name)
            
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
         

    def update_weights(self, desired_score, actual_score, f_scores):
        """ Compare the difference between the predicted game state
        and the current game state and update the weights.
        The update formula is: 
        
        new_weight = current_weight + n*(desire_score - actual_score)*f_score
        """
        for i in range(len(self.weights)):
            if i != 8 or i != 9:
                self.weights[i] = self.weights[i] + self.learning_rate*(desired_score - actual_score)*f_scores[i]     



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

## url handlers

class new_game(object):
  
  def POST(self):
    p = load_current_player()
    games = waiting_players()
    games.add(p.name)
    try:
      f = open('state/waiting_players', 'w')
      cPickle.dump(games, f)
    except:
      f.close()
    print web.seeother("/waiting/")

class join_game(object):
  
  def POST(self):
    p = load_current_player()
    wi = web.input()
    opponent = HumanPlayer.load(wi['opponent'])
    game = twixt.Twixt(opponent.name, p.name, (10,10))
    game.id = sha.sha(game.player1 + game.player2).hexdigest()
    p.game_id        = game.id
    opponent.game_id = game.id
    p.save(), opponent.save()
    game.current_player = game.player1
    render_game_board_image(game)
    save_game(game)
    web.seeother("/play/")

class waiting(object):
  def GET(self):
    p = load_current_player()
    if hasattr(p, 'game_id'):
      print web.seeother("/play/")
    else:
      print render.waiting()

class play(object):
  def POST(self):
    wi = web.input()
    p = load_current_player()
    g = load_game(p.game_id)
    if g.current_player == p.name:
      import re
      m = re.match("([0-9]+)\,([0-9]+)", wi['twixt_node'])
      move = (int(m.group(1)), int(m.group(2)))
      try:
        g.claim_node(move, p.name)
        render_game_board_image(g)
        g.current_player = g.opponent(p.name)
        save_game(g)
      except twixt.NodeError, e:
        sys.stderr.write(repr(e))
    web.seeother("/play/")
  
  def GET(self):
    p = load_current_player()
    g = load_game(p.game_id)
    if g.current_player == p.name:
      print render.game_move(g, p, area_tags(g))
    else:
      print render.game_wait(g, p)

class login(object):
  
  def POST(self):
    # need to persist player.
    #  player should get a random cookie, to identify himself with.
    wi = web.input()
    # need to check if player already exists...
    p = HumanPlayer(wi['name'], wi['password']).save()
    web.setcookie("name", p.name)
    web.setcookie("secret", p.secret)
    print web.seeother("/")
  
  def GET(self, name):
    print web.redirect("/")


class index(object):
  
  def GET(self):
    try:
      p = load_current_player()
    except PlayerExistsException:
      p = None
    if p is not None:
      print render.lobby(p.name, waiting_players())
    else:
      print render.index()



if __name__ == "__main__":
  web.webapi.internalerror = web.debugerror
  web.run(urls, globals(), web.reloader)
