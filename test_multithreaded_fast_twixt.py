# test_fast_twixt.py
import hotshot
import timeit
from play_fast_twixt import render_game_board_image
from fast_twixt import *

test_state = copy.deepcopy(root_state)
claim((0,4), 'p1', test_state)
claim((3,0), 'p2', test_state)
claim((2,3), 'p1', test_state)
claim((2,2), 'p2', test_state)
claim((4,2), 'p1', test_state)
claim((1,5), 'p2', test_state)
claim((5,4), 'p1', test_state)

print zeta("p1", test_state)
print zeta("p2", test_state)

render_game_board_image("test.png", test_state)

assert there_are_no_remaining_unreserved_nodes_in(test_state) == False

assert the_winner_is("p1", test_state) == True
assert there_is_a_winner_for(test_state) == True
assert there_are_no_remaining_unreserved_nodes_in(test_state) == False
assert is_terminal(test_state) == True

assert 5.75 < zeta("p1", test_state) < 6.25
assert -2.75 < zeta("p2", test_state) < 3.25

print heuristic_value_of(test_state)
assert 38.75 < heuristic_value_of(test_state) < 39.25

assert intersects([(1,1), (3,2)], [(2,1), (0,2)]) == True
assert intersects([(1,1), (3,2)], [(2,1), (4,0)]) == False

test_state = copy.deepcopy(root_state)
claim((2,4), 'p1', test_state)
claim((1,3), 'p2', test_state)
claim((3,1), 'p1', test_state)

test_state['p1'][4,3] = []
assert attempt_to_connect((2,4), (4,3), 'p1', test_state) == True
assert autoconnect_others_to((4,3), 'p1', test_state) == 1

test_state['p2'][3,4] = []
assert attempt_to_connect((1,3), (3,4), 'p2', test_state) == False
assert autoconnect_others_to((3,4), 'p2', test_state) == 0

old_test_state = copy.deepcopy(test_state)
test_state['p1'][1,2] = []
autoconnect_others_to((1,2), 'p1', test_state)
assert state_hash(old_test_state) != state_hash(test_state)
disconnect_others_from((1,2), 'p1', test_state)
assert state_hash(old_test_state) == state_hash(test_state)



test_state = copy.deepcopy(root_state)
claim((3,3), "p1", test_state)
claim((2,2), "p2", test_state)
claim((5,4), "p1", test_state)
claim((3,4), "p2", test_state)
old_test_state = copy.deepcopy(test_state)

best_move = threaded_get_next_move("p1", test_state)
assert state_hash(old_test_state) == state_hash(test_state)

test_state["p1"][1,2] = []
assert autoconnect_others_to((1,2), "p1", test_state) == 0

print "all tests passed."

# import hotshot, hotshot.stats
# 
# prof = hotshot.Profile("stones.prof")
# prof.run("get_next_move('p1', test_state)")
# prof.close()
# stats = hotshot.stats.load("stones.prof")
# stats.strip_dirs()
# stats.sort_stats('time', 'calls')
# stats.print_stats(20)