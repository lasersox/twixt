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
  f = open("state/game_%s.pickle" % game_id)
  g = cPickle.load(f)
  f.close()
  return g

def save_game(game):
  try:
    f = open("state/game_%s.pickle" % game.id, 'w')
    cPickle.dump(game, f)
    f.close()
  except:
    f.close()
  del f

def waiting_players():
  if os.path.exists('state/waiting_players.pickle'):
    f = open('state/waiting_players.pickle')
    games = cPickle.load(f)
    f.close()
  else:
    games = set([])
  return games

## url handlers

class new_game(object):
  
  def POST(self):
    p = load_current_player()
    games = waiting_players()
    games.add(p.name)
    try:
      f = open('state/waiting_players.pickle', 'w')
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
