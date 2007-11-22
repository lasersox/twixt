import sys, os
sys.path.append(os.getcwd())

from pytwixt import node_twixt as twixt
from twixt_heuristic import *
from index import render_game_board_image

g = twixt.Twixt("foo", "bar", (5, 5))
g.id = "test_Twixt"

next_states = get_next_states(g, 'foo', 2)

render_game_board_image(g)
for i,node in enumerate(next_states[1]):
    g = node[0]
    g.id = "recur_%i" % i
    print g.id
    # render_game_board_image(g)
    for j,child_node in enumerate(node[1]):
        #print child_node
        child_g = child_node[0]
        child_g.id = "recur_%i_%i" % (i,j)
        print child_g.id
        #render_game_board_image(child_g)
        # for k,child_child_node in enumerate(child_node[1]):
        #     #print child_node
        #     child_child_g = child_child_node[0]
        #     child_child_g.id = "recur_%i_%i_%i" % (i,j,k)
        #     # render_game_board_image(child_child_g)
print 

