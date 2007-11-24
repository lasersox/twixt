import sys, os

sys.path.append(os.chdir("../"))
sys.path.append(os.getcwd())


from pytwixt import node_twixt as twixt
from index import render_game_board_image
from twixt_heuristic import *

g = twixt.Twixt("foo", "bar", (10, 10))
g.id = "test"

g.claim_node((2,2), 'foo')
g.claim_node((4,3), 'bar')
g.claim_node((3,4), 'foo')
g.claim_node((6,2), 'bar')
g.claim_node((2,6), 'foo')
render_game_board_image(g)

""" Test 1: Total bridge length """
print "Player %s:  Total bridge length %s." % ('foo', f_1(g,'foo'))
print "Player %s:  Total bridge length %s." % ('bar', f_1(g,'bar'))

# pass

""" Test 2 """
print "Player %s - %s:  Difference %s." % ('foo', g.opponent('foo'), f_2(g,'foo'))
print "Player %s - %s:  Difference %s." % ('bar', g.opponent('bar'), f_2(g,'bar'))

#pass

""" Test 3 """
print "Player %s:  longest bridge length %s." % ('foo', f_3(g,'foo'))
print "Player %s:  longest bridge length %s." % ('bar', f_3(g,'bar'))

# not pass
# fixed bug, working now

""" Test 4 """
print "Player %s:  vertical length %s." % ('foo', f_4(g,'foo'))
print "Player %s:  vertical length %s." % ('bar', f_4(g,'bar'))
#not pass
# fixed bug : floating point operation


""" Test 5 """
print "Player %s:  horizontal length %s." % ('foo', f_5(g,'foo'))
print "Player %s:  horizontal length %s." % ('bar', f_5(g,'bar'))

#not pass
# fixed bug : floating point operation

""" Test 6 """
print "Player %s:  inverse vertical length %s." % ('foo', f_6(g,'foo'))
print "Player %s:  inverse vertical length %s." % ('bar', f_6(g,'bar'))

#pass

""" Test 7 """
print "Player %s:  inverse horizontal length %s." % ('foo', f_7(g,'foo'))
print "Player %s:  inverse horizontal length %s." % ('bar', f_7(g,'bar'))

#pass

""" Test 8 """
print "Player %s:  extendable nodes %s." % ('foo', f_8(g,'foo'))
print "Player %s:  extendable nodes %s." % ('bar', f_8(g,'bar'))
#not pass
# fixed bug : floating point operation




