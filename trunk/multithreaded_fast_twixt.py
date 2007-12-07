# coding: utf-8
import sys, cPickle, subprocess, copy, random, time, itertools
from math import *

LOG = file("/tmp/twixt.log", "w")

width, height = 6,6
game_nodes = set((x,y) for x in range(width) for y in range(height) if not x % (width-1) + y % (height-1) == 0)

starting_nodes = {
    "p1" : set((0,y) for y in range(1,height-1)),
    "p2" : set((x,0) for x in range(1,width-1))}
finishing_nodes = {
    "p1" : set((width-1,y) for y in range(1,height-1)),
    "p2" : set((x,height-1) for x in range(1,width-1))}
reserved_nodes = {
    "p1" : starting_nodes['p1'].union(finishing_nodes['p1']),
    "p2" : starting_nodes['p2'].union(finishing_nodes['p2'])}

# root_state = {"p1" : {"nodes": set(), "connections": {}},
#               "p2" : {"nodes": set(), "connections": {}}}

root_state = {"p1" : {},
              "p2" : {}}

def state_hash(state):
    return hash(tuple([ 
        (node, tuple(sorted(connected_nodes))) \
        for node, connected_nodes in itertools.chain(['p1'], sorted(state['p1'].iteritems()), ['p2'], sorted(state['p2'].iteritems()))
    ]))

def claim(node, player, state):
    if node in state['p1'] or node in state['p2'] or node in reserved_nodes[opponent_of(player)]:
        raise Exception("Can't claim this node.")
    autoconnect_others_to(node, player, state)
    
def opponent_of(player): return 'p1' if player == 'p2' else 'p2'

def the_winner_is(player, state):
    _starting_nodes  =  starting_nodes[player].intersection(state[player].keys())
    _finishing_nodes = finishing_nodes[player].intersection(state[player].keys())
    _connections     = state[player]
    
    if not (_starting_nodes or _finishing_nodes or _connections): return False
    
    marked = set()
    stack = []
    
    # perform search
    for node in _starting_nodes:
        marked.add(node)
        stack.append(node)
    while len(stack):
        current_node = stack.pop()
        if not _connections[current_node]: continue
        for node in _connections[current_node]:
            if node in _finishing_nodes:
                return True
            if not node in marked:
                marked.add(node)
                stack.append(node)
    return False
    

def there_is_a_winner_for(state):
    return True if the_winner_is("p1", state) or the_winner_is("p2", state) else False

def there_are_no_remaining_unreserved_nodes_in(state):
    t = game_nodes.difference(state['p1'].keys() + state['p2'].keys() + list(reserved_nodes['p1']) + list(reserved_nodes['p2']))
    return True if not t else False
    
def is_terminal(state):
    if there_is_a_winner_for(state):
        return True
    elif there_are_no_remaining_unreserved_nodes_in(state):
        return True
    else:
        return False

def zeta(player, state):
    """ Greatest distance between reserved edges covered by a single connected path. """
    
    _connections = state[player]
    # if not _connections: return 0
    
    if player == "p1":
        project = lambda node: node[0]
        axis = width
    elif player == "p2":
        project = lambda node: node[1]
        axis = height

    projection = [0] * axis
        
    longest_length = 0.
    marked = set()
    
    for node in state[player].keys():
        if node in marked: continue
        this_path = set([node])
        marked.add(node)
        stack = [node]
        # get all nodes connected to this node by a path
        while len(stack):
            current_node = stack.pop()
            for other_node in _connections[current_node]:
                if not other_node in marked:
                    marked.add(other_node)
                    stack.append(other_node)
                    this_path.add(other_node)
        projection = set(project(_node) for _node in this_path)
        path_length = max(projection) - min(projection)
        if path_length > longest_length:
            longest_length = path_length + 1.
    return longest_length
    
def heuristic_value_of(state):
    return width*height * the_winner_is("p1", state) + zeta("p1", state) + random.uniform(0, 0.05)\
            - width*height * the_winner_is("p2", state) - zeta("p2", state) - random.uniform(0, 0.05)

def intersects(connection, blocker):
    """
    True if conn0 intersects conn1 on the domains of each of the two lines. (The
    domain of the line is the region of the x-axis between the two endpoints of
    the line).
    """
    # this function solves two bounded lines for the point of intersection.
    # if (x,y) is in the domain of both of the lines this function return true.
    cslope = float(connection[0][1] - connection[1][1]) / (connection[0][0] - connection[1][0])
    bslope = float(blocker[0][1] - blocker[1][1]) / (blocker[0][0] - blocker[1][0])
    if cslope != bslope: # check for parallelism.
        dm = float(cslope - bslope)
        cintercept = float(connection[0][1] - cslope * connection[0][0])
        bintercept = float(blocker[0][1] - bslope * blocker[0][0])
        db = float(cintercept - bintercept)
        ix = -db/dm # solving for x
        iy = cslope*ix + cintercept # solving for y.
        # now we have the point of interception but is it on the domain
        # of **both** lines?
        cdomain = sorted([connection[0][0], connection[1][0]])
        bdomain = sorted([blocker[0][0], blocker[1][0]])
        if cdomain[0] < ix and cdomain[1] > ix and bdomain[0] < ix and bdomain[1] > ix:
            # the point of intersection is on the domain of both lines.
            return True
    # slopes are equal, or the point of intersection is not on the domain
    # of both lines.
    return False

__autoconnect_differentials = [(1,2), (1,-2), (-1,2), (-1,-2),
                              (2,1), (-2,1), (2,-1), (-2,-1)]

def attempt_to_connect(node, other_node, player, state):
    # make connection from node to other_node,
    # returning False if the connection is blocked
    # and True if the connection is made.
    _player = state[player]
    _other_player = state[opponent_of(player)]
    xs = sorted([node[0], other_node[0]])
    ys = sorted([node[1], other_node[1]])
    potential_blockers = set([(xs[0], ys[0]), (xs[1], ys[0]),
                              (xs[0], ys[1]), (xs[1], ys[1]),
                              (xs[0] + (xs[1] - xs[0])/2, ys[0]), (xs[0] + (xs[1] - xs[0])/2, ys[1]),
                              (xs[0], ys[0] + (ys[1] - ys[0])/2), (xs[1], ys[0] + (ys[1] - ys[0])/2)])
    potential_blockers.difference_update((node, other_node))
    potential_blockers.intersection_update(_other_player.keys())
    while len(potential_blockers):
        blocker = potential_blockers.pop()
        if blocker not in _other_player: continue
        for other_blocker in _other_player[blocker]:
            if intersects([node, other_node], [blocker, other_blocker]):
                return False
    # make the connection
    _player[node].append(other_node)
    _player[other_node].append(node)
    return True
        
def autoconnect_others_to(node, player, state):
    # autoconnect all other possilbe nodes to node.
    number_connected = 0
    if node not in state[player]:
        state[player][node] = []
    for dx,dy in __autoconnect_differentials:
        other_node = (node[0]+dx, node[1]+dy)
        if not other_node in state[player]: continue
        if other_node in state[player][node] and node in state[player][other_node]: continue
        if attempt_to_connect(other_node, node, player, state):
            number_connected += 1
    return number_connected

def disconnect_others_from(node, player, state):
    if node not in state[player]: return
    for other_node in state[player][node]:
        state[player][other_node].remove(node)
    del state[player][node]


def min_dist_from_players_nodes(nodes, player, state):
    num_player_nodes = len(state[player].keys())
    for node in nodes:
        _min = None
        for other in state[player]:
            dist = sqrt((node[0]-other[0])**2 + (node[1] - other[1])**2)
            if dist < _min or _min == None:
                _min = dist
        yield _min
    
def available_nodes(player, state):
    return game_nodes \
                        .difference(state['p1'].keys()) \
                        .difference(state['p2'].keys()) \
                        .difference(reserved_nodes[opponent_of(player)])
    
    # if not state[player]['nodes']:
    # for node in available_nodes: yield node
    
    # avg_distance_from_players_nodes = list(min_dist_from_players_nodes(available_nodes, player, state))
    # for min_dist, node in sorted(zip(avg_distance_from_players_nodes, available_nodes)):
    #     yield node
        
def negamax(player, state, depth, alpha, beta, explored=set()):
    if is_terminal(state) or depth == 0:
        score = heuristic_value_of(state)
        if score == 0 and isinstance(score, int):
            LOG.write(str(depth) + str(state))
            raise Exception
        return score
    else:
        for node in available_nodes(player, state):
            old = state_hash(state)
            autoconnect_others_to(node, player, state)
            if state_hash(state) in explored:
                disconnect_others_from(node, player, state)
                # del state[player][node]
                continue
            explored.add(state_hash(state))
            score = -negamax(opponent_of(player), state, depth-1, -beta, -alpha, explored)
            disconnect_others_from(node, player, state)
            assert old == state_hash(state)
            alpha = max(alpha, score)
            if alpha >= beta:
                return beta
        return alpha

def negamax_subprocess(node, player, state, depth, alpha, beta):
    p = subprocess.Popen([sys.executable, "-u",  __file__], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(cPickle.dumps((node, player, state, depth, alpha, beta)))
    p.stdin.close()
    return p

def threaded_get_next_move(player, state, depth=3, concurrency=2):
    
    best_node, best_score = None, -100
    nodes_to_check = set(available_nodes(player, state))
    thread_buffer = []
    
    while nodes_to_check:

        for p in thread_buffer:
            if p.poll() is not None:
                thread_buffer.remove(p)
                node, score = cPickle.loads(p.stdout.read())
                print "    ", node, repr(score)
                # p.stdout.close()
                if score > best_score:
                    best_node, best_score = node, score
                del p
        
        while len(thread_buffer) < concurrency:
            node = nodes_to_check.pop()
            autoconnect_others_to(node, player, state)
            p = negamax_subprocess(node, opponent_of(player), state, depth-1, -100., 100.)
            thread_buffer.append(p)
            disconnect_others_from(node, player, state)
        # no reason to loop as fast as possible, sleep a bit.
        time.sleep(0.01)
        
    return best_node

# def negamax_stacked(state, depth, alpha, beta, explored=set()):
#     stack = [(state, None)]
#     while len(stack):
#         current_state = stack.pop()
#         if is_terminal(current_state) or depth == 0:
#             return heuristic_value_of(current_state)
#         else:
#             for child in children_of(current_state):
#                 if state_hash(child) in explored: continue
#                 explored.add(current_state_hash(child))
#                 stack.append(child)
#                 score = -negamax(child, depth-1, -beta, -alpha, explored)
#                 alpha = max(alpha, score)
#                 if alpha >= beta:
#                     return beta
#             return alpha


if __name__ == "__main__":
    import sys, cPickle
    node, player, state, depth, alpha, beta = cPickle.loads(sys.stdin.read())
    score = -negamax(player, state, depth, alpha, beta)
    sys.stdout.write(cPickle.dumps((node, score)))
    sys.exit(0)
