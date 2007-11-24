import sys, os

sys.path.append(os.chdir("../"))
sys.path.append(os.getcwd())


from pytwixt import node_twixt as twixt
from index import render_game_board_image

g = twixt.Twixt("foo", "bar", (10, 10))
g.id = "test"

g.claim_node((2,2), 'foo')
g.claim_node((4,3), 'bar')
g.claim_node((3,4), 'foo')
g.claim_node((6,2), 'bar')
g.claim_node((2,6), 'foo')

render_game_board_image(g)
