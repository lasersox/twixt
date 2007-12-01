# test_fast_twixt.py
import hotshot
import timeit
from fast_twixt import *

test_state = copy.deepcopy(root_state)
claim((0,5), 'p1', test_state)
claim((2,4), 'p1', test_state)
claim((4,5), 'p1', test_state)
claim((6,4), 'p1', test_state)
claim((7,6), 'p1', test_state)


assert the_winner_is("p1", test_state) == True
assert there_is_a_winner_for(test_state) == True
assert there_are_no_remaining_unreserved_nodes_in(test_state) == False
assert is_terminal(test_state) == True

assert 8 <= zeta("p1", test_state) < 9
assert 0 <= zeta("p2", test_state) < 1

assert 8 <= heuristic_value_of(test_state) < 9

assert intersects([(1,1), (3,2)], [(2,1), (0,2)]) == True
assert intersects([(1,1), (3,2)], [(2,1), (4,0)]) == False

test_state = copy.deepcopy(root_state)
claim((2,4), 'p1', test_state)
claim((4,5), 'p1', test_state)
claim((6,4), 'p1', test_state)
claim((2,6), 'p2', test_state)
claim((1,4), 'p2', test_state)
claim((4,3), 'p2', test_state)

test_state['p1']['nodes'].add((7,2))
assert attempt_to_connect((5,2), (7,3), 'p1', test_state) == True
assert autoconnect_others_to((7,2), 'p1', test_state) == 1

test_state['p2']['nodes'].add((5,2))
assert attempt_to_connect((5,2), (7,3), 'p2', test_state) == False
assert autoconnect_others_to((5,2), 'p2', test_state) == 0

test_state = copy.deepcopy(root_state)
claim((2,4), 'p1', test_state)
claim((4,5), 'p1', test_state)
claim((2,6), 'p2', test_state)
claim((1,4), 'p2', test_state)

old_test_state = copy.deepcopy(test_state)
test_state['p1']['nodes'].add((0,3))
autoconnect_others_to((0,3), 'p1', test_state)
disconnect_others_from((0,3), 'p1', test_state)
test_state['p1']['nodes'].remove((0,3))
assert state_hash(old_test_state) == state_hash(test_state)

def get_next_move(player, state):
    depth = 3
    best_node, best_score = None, -10
    worst_node, worst_score = None, 10
    for node in available_nodes(player, state):
        state[player]['nodes'].add(node)
        autoconnect_others_to(node, player, state)
        score = (-1 if depth % 2 else 1) * negamax(state, depth, -9, 9)
        disconnect_others_from(node, player, state)
        state[player]['nodes'].remove(node)
        if score > best_score:
            best_node, best_score = node, score
        if score < worst_score:
            worst_node, worst_score = node, score

    print "best_move: %r, score: %i" % (best_node, best_score)
    print "worst_move: %r, score: %i" % (worst_node, worst_score)

print timeit.Timer("get_next_move('p1', test_state)", "from __main__ import get_next_move, test_state").timeit(1)

# import hotshot, hotshot.stats
# 
# prof = hotshot.Profile("stones.prof")
# prof.run("get_next_move('p1', test_state)")
# prof.close()
# stats = hotshot.stats.load("stones.prof")
# stats.strip_dirs()
# stats.sort_stats('time', 'calls')
# stats.print_stats(20)