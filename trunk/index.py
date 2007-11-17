# coding: utf-8

import os, cPickle
import sha
import web
from pytwixt import node_twixt as twixt


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

def render_game_board(game):
  try:
    import Image, ImageDraw
  except ImportError:
    raise ImportError("Execution failed because the required “Python Imaging Library” is missing.\n"\
                     "Get it here: http://www.pythonware.com/products/pil/\n")
  
  player_color = {game.player1 : "#4444FF", game.player2: "#FF4444", "": "#aaaaaa"}
  
  m = 32
  r = 4
  
  size = (game.size[0] + 1) * m, (game.size[1] + 1) * m
  im = Image.new("RGB", size)
  
  try:
    import aggdraw
    draw = aggdraw.Draw(im)
    p = aggdraw.Pen("black", 1)
    player_brush = {game.player1 : aggdraw.Brush(player_color[game.player1]),
                    game.player2 : aggdraw.Brush(player_color[game.player2]),
                    ""           : aggdraw.Brush(player_color[''])}
    print "Using aggdraw..."
  except ImportError:
    aggdraw = None
    draw = ImageDraw.Draw(im)
  
  if aggdraw is not None:
    draw.rectangle([0, 0, size[0], size[1]], aggdraw.Brush("white"))
  else:
    draw.rectangle([0, 0, size[0], size[1]], fill="#FFFFFF")
  
  left_top = lambda nd: (int(m*(nd.x+1) - r), int(m*(nd.y+1) + r))
  left_bot = lambda nd: (int(m*(nd.x+1) - r), int(m*(nd.y+1) - r))
  righ_top = lambda nd: (int(m*(nd.x+1) + r), int(m*(nd.y+1) + r))
  righ_bot = lambda nd: (int(m*(nd.x+1) + r), int(m*(nd.y+1) - r))
  
  for node in game.nodes.values():
    print "Drawing %s..." % node
    owner = node.owner
    box = left_bot(node) + righ_top(node)
    if aggdraw is not None:
      draw.ellipse(box, p, player_brush[node.owner])
    else:
      draw.ellipse(box, fill=player_color[node.owner], outline="#000000")
  
  if aggdraw is not None:
    draw.flush()
  del draw
  im.save("./static/%s.png" % game.id)

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

def load_current_game(p):
  try:
    f = open("state/game_%s" % p.game_id, 'w')
    g = cPickle.load(game, f)
  except:
    f.close()
    raise GameError("Could not open game state.")
  return g

def save_game(game):
  try:
    f = open("state/game_%s" % game.id, 'w')
    cPickle.dump(game, f)
  except:
    f.close()

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
  pass

class HumanPlayer(Player):
  
  def __init__(self, name, secret):
    self.name   = name
    self.secret = sha.sha(secret).hexdigest()
  
  def save(self):
    f = open("state/player_%s" % sha.sha(self.name).hexdigest(), 'w')
    cPickle.dump(self, f)
    f.close()
    return self
  
  @staticmethod
  def load(name):
    fname = "state/player_%s" % sha.sha(name).hexdigest()
    if os.path.exists(fname):
      f = open(fname)
      p = cPickle.load(f)
      return p
    else:
      raise PlayerExistsException("No such player exists.")
  
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
  	
  	def __init__(self, name):
    	self.name = name
  	
  	def next_move(self, game):
    	(x,y) = (1,1)
    	return (x,y)

class ThanhsComputerPlayer(ComputerPlayer):
  	pass

class LanfrancosComputerPlayer(ComputerPlayer):
    pass

class AlexsComputerPlayer(ComputerPlayer):
  	pass

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
    game = twixt.Twixt(opponent.name, p.name)
    game.id = sha.sha(game.player1 + game.player2).hexdigest()
    p.game_id        = game.id
    opponent.game_id = game.id
    p.save(), opponent.save()
    game.current_player = game.player1
    render_game_board(game)
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
    p = load_current_player()
    g = load_current_game(p)
  
  
  def GET(self):
    p = load_current_player()
    g = load_current_game(p)
    if g.current_player == p.name:
      print render.game_move(g, p)
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
