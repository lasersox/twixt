# coding: utf-8

from fast_twixt import *
MacOS = None
try: import MacOS
except: pass
import copy
import time

NODE_SPACING = 40
NODE_RADIUS  = 5

def render_game_board_image(file_name, state, size=(8,8)):
    try:
        import Image, ImageDraw
    except ImportError:
        raise ImportError("Execution failed because the required “Python Imaging Library” is missing.\n"\
                     "Get it here: http://www.pythonware.com/products/pil/\n")
  
    player_color = {'p1' : "#4444FF", 'p2': "#FF4444", "": "#aaaaaa"}

    m = NODE_SPACING
    r = NODE_RADIUS

    size = (width + 1) * m, (height + 1) * m
    im = Image.new("RGB", size)
  
    try:
        import aggdraw
        draw = aggdraw.Draw(im)
        p = aggdraw.Pen("black", 1)
        player_brush = {"p1" : aggdraw.Brush(player_color["p1"]),
                        "p2" : aggdraw.Brush(player_color["p2"]),
                        ""           : aggdraw.Brush(player_color[''])}
        player_pen = {"p1" : aggdraw.Pen(player_color["p1"], width=2),
                      "p2" : aggdraw.Pen(player_color["p2"], width=2),
                      ""           : aggdraw.Pen(player_color[''], width=2)}
        # print "Using aggdraw..."
    except ImportError:
        aggdraw = None
        draw = ImageDraw.Draw(im)
  
    left_top = lambda nd: (int(m*(nd[0]+1) - r), int(m*(nd[1]+1) + r))
    left_bot = lambda nd: (int(m*(nd[0]+1) - r), int(m*(nd[1]+1) - r))
    righ_top = lambda nd: (int(m*(nd[0]+1) + r), int(m*(nd[1]+1) + r))
    righ_bot = lambda nd: (int(m*(nd[0]+1) + r), int(m*(nd[1]+1) - r))

    center = lambda nd: (int(m*(nd[0]+1)), int(m*(nd[1]+1)))
    class point(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
    if aggdraw is not None:
        draw.rectangle([0, 0, size[0], size[1]], aggdraw.Brush("white"))
        draw.line(center(point(0,0.5))  + center(point(size[0]-1,0.5)),  player_pen["p2"])
        draw.line(center(point(0,size[1]-1.5))   + center(point(size[0]-1,size[1] - 1.5)), player_pen["p2"])
        draw.line(center(point(0.5,0))    + center(point(0.5,size[1]-1)),  player_pen[game.player1])
        draw.line(center(point(size[0]-1.5,0))   + center(point(size[0]-1.5,size[1]-1)), player_pen["p1"])
    else:
        draw.rectangle([0, 0, size[0], size[1]], fill="#FFFFFF")
  
    for player in ['p1', 'p2']:
        for node in state[player].keys():
            for other_node in state[player][node]:
                if aggdraw is not None:
                    draw.line(center(node) + center(other_node), player_pen[player])
                else:
                    draw.line([center(node), center(other_node)], fill=player_color[player], width=4)
  
        for node in state[player].keys():
            # print "Drawing %s..." % node
            box = left_bot(node) + righ_top(node)
            if aggdraw is not None:
                draw.ellipse(box, p, player_brush[player])
            else:
                draw.ellipse(box, fill=player_color[player], outline="#000000")
  
    if aggdraw is not None:
        draw.flush()
    del draw
    im.save(file_name)

if __name__ == "__main__":
    state = copy.deepcopy(root_state)
    i = 0
    while not is_terminal(state):
        print "Asking the computer for his move..."
        best_move = None
        before = time.time()
        best_move = get_next_move('p1', state, 6)
        after = time.time()
        autoconnect_others_to(best_move, 'p1', state)
        print "Computer claimed %s in %f minutes." % (str(best_move), (after - before)/60)
        if is_terminal(state): break
        human_has_not_moved = True
        if MacOS:
            MacOS.SysBeep()
        while human_has_not_moved:
            try:
                _possible_move = input("Enter your move:")
            except SyntaxError:
                print "Use `(x,y)' format."
                continue
            autoconnect_others_to(_possible_move, 'p2', state)
            human_has_not_moved = False
        render_game_board_image("turn_%i.png" % i, state, size=(width,height))
        i += 1
    if the_winner_is("p2", state):
        print "You've Won!"
    elif the_winner_is("p1", state):
        print "The Computer has won!"
    else:
        print "Stalemate!"