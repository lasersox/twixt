# coding: utf-8
import sys, cPickle, subprocess, copy, random, time, itertools, operator
from math import *

INF = float(sys.maxint)
NUMBER_TRANSPOSITIONS = 250000

width, height = 8,8

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

def new_game():
    return {"p1" : {}, "p2" : {}}

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
    
def heuristic_value_of(player, state):
    player_score = zeta(player, state)**2 + random.uniform(0, 0.05)
    opponent_score = zeta(opponent_of(player), state)**2 + random.uniform(0, 0.05)
    return player_score - opponent_score

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

def available_nodes(player, state, trans):
    available_nodes = list(game_nodes \
                        .difference(state['p1'].keys()) \
                        .difference(state['p2'].keys()) \
                        .difference(reserved_nodes[opponent_of(player)]))
    # return available_nodes
    next_scores = []
    for node in available_nodes:
        autoconnect_others_to(node, player, state)
        _hash = state_hash(state)
        next_scores.append(trans[_hash % NUMBER_TRANSPOSITIONS][2] if _hash % NUMBER_TRANSPOSITIONS in trans and trans[_hash % NUMBER_TRANSPOSITIONS][0] == _hash else 0.)
        disconnect_others_from(node, player, state)
    ordered_nodes = map(operator.itemgetter(1), sorted(zip(next_scores, available_nodes), reverse=True))
    return ordered_nodes
    
    
    # if not state[player]['nodes']:
    # for node in available_nodes: yield node
    
    # avg_distance_from_players_nodes = list(min_dist_from_players_nodes(available_nodes, player, state))
    # for min_dist, node in sorted(zip(avg_distance_from_players_nodes, available_nodes)):
    #     yield node
        
def negamax(player, state, depth, alpha, beta, transpositions, max_depth):
    global nodes_searched
    if the_winner_is(player, state):
        return INF
    elif the_winner_is(opponent_of(player), state):
        return -INF
    elif depth == 0:
        return heuristic_value_of(player, state)
    else:
        for node in available_nodes(player, state, transpositions):
            autoconnect_others_to(node, player, state)
            _hash = state_hash(state)
            if _hash % NUMBER_TRANSPOSITIONS in transpositions \
                    and transpositions[_hash % NUMBER_TRANSPOSITIONS][0] == _hash \
                    and transpositions[_hash % NUMBER_TRANSPOSITIONS][1] > max_depth:
                continue
            score = -negamax(opponent_of(player), state, depth-1, -beta, -alpha, transpositions, max_depth)
            nodes_searched += 1
            transpositions[_hash % NUMBER_TRANSPOSITIONS] = (_hash, max_depth, score)
            disconnect_others_from(node, player, state)
            alpha = max(alpha, score)
            if alpha >= beta:
                return beta
        return alpha

def _subprocess(*args):
    p = subprocess.Popen([sys.executable, "-u",  __file__], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(cPickle.dumps(args))
    p.stdin.close()
    return p

def plain_get_next_move(player, state, max_depth):
    nodes_searched = 0
    start_time = time.time()
    print 
    transpositions = {}

    best_node, best_score = None, -INF
    for depth in range(1, max_depth+1):
        nodes_to_check = available_nodes(player, state, transpositions)
        alpha = -INF
        beta  = INF
        while nodes_to_check:
            node = nodes_to_check.pop(0)
            autoconnect_others_to(node, player, state)
            _hash = state_hash(state)
            nodes_searched += 1
            score = -negamax(opponent_of(player), state, depth-1, -beta, -alpha, transpositions, depth)
            sys.stdout.write("."); sys.stdout.flush()
            disconnect_others_from(node, player, state)
            transpositions[_hash % NUMBER_TRANSPOSITIONS] = (_hash, depth, score)
            alpha = max(alpha, score)
            if score > best_score:
                best_node, best_score = node, score
            if alpha >= beta:
                # we have found a winning move... get rid of the rest of the nodes to search
                nodes_to_check = set()
                break
    end_time = time.time()
    sys.stdout.write("\n")
    print "Best move: ", repr(best_node), best_score
    print "# nodes_searched: ", nodes_searched
    print "Time spent: ", end_time - start_time
    return best_node

def _threaded_get_next_move(player, state, depth, concurrency=2):
    start_time = time.time()
    print 
    transpositions = {}
    best_node, best_score = None, -INF
    nodes_to_check = available_nodes(player, state, transpositions)
    
    for depth in range(1, depth+1):
        nodes_to_check = copy.deepcopy(nodes_to_check)
        thread_buffer = []
        
        while nodes_to_check or thread_buffer:

            for p in thread_buffer:
                if p.poll() is not None:
                    thread_buffer.remove(p)
                    node, score, _transpositions = cPickle.loads(p.stdout.read())
                    transpositions.update(_transpositions)
                    print "    ", node, repr(score)
                    # p.stdout.close()
                    if score > best_score:
                        best_node, best_score = node, score
                    if score == sys.maxint:
                    #     # we have found a winning move... get rid of the rest of the nodes to search
                        nodes_to_check = set()
                    del p
        
            if nodes_to_check:
                while len(thread_buffer) < concurrency:
                    node = nodes_to_check.pop(0)
                    autoconnect_others_to(node, player, state)
                    p = _subprocess(node, opponent_of(player), state, depth-1, -INF, INF, transpositions, depth)
                    thread_buffer.append(p)
                    disconnect_others_from(node, player, state)
        
        if best_score == INF:
            break
        # no reason to loop as fast as possible, sleep a bit.
        # time.sleep(0.01)
    end_time = time.time()
    print "Best move: ", repr(best_node), best_score
    print "Time spent: ", end_time - start_time
    return best_node

def threaded_get_next_move(player, state, max_depth, concurrency=2):
    nodes_searched = 0
    start_time = time.time()

    best_node, best_score = None, -INF    
    nodes_to_check = available_nodes(player, state, {})    

    # should code this to work for arbitrary # of subprocesses, but 2 will do for now. 
    p1 = _subprocess(player, state, nodes_to_check[:len(nodes_to_check)/2], max_depth)
    p2 = _subprocess(player, state, nodes_to_check[len(nodes_to_check)/2:], max_depth)

    thread_buffer = [p1, p2]
    while thread_buffer:
        for p in thread_buffer:
            if p.poll() is not None:
                thread_buffer.remove(p)
                node, score, _nodes_searched  = cPickle.loads(p.stdout.read())
                nodes_searched += _nodes_searched
                print node, score
                if score > best_score:
                    best_node, best_score = node, score
                del p

    end_time = time.time()
    print "Best move: ", repr(best_node), best_score
    print "# nodes searched: ", nodes_searched
    print "Time spent: ", end_time - start_time
    return best_node


# def negamax_stacked(state, depth, alpha, beta, transpositions=set()):
#     stack = [(state, None)]
#     while len(stack):
#         current_state = stack.pop()
#         if is_terminal(current_state) or depth == 0:
#             return heuristic_value_of(current_state)
#         else:
#             for child in children_of(current_state):
#                 if state_hash(child) in transpositions: continue
#                 transpositions.add(current_state_hash(child))
#                 stack.append(child)
#                 score = -negamax(child, depth-1, -beta, -alpha, transpositions)
#                 alpha = max(alpha, score)
#                 if alpha >= beta:
#                     return beta
#             return alpha


if __name__ == "__main__":
    global nodes_searched
    nodes_searched = 0
    import sys, cPickle
    player, state, nodes_to_check, max_depth = cPickle.loads(sys.stdin.read())
    best_node, best_score = None, -INF
    alpha, beta = -INF, INF
    transpositions = {}
    for depth in range(1, max_depth+1):
        for node in nodes_to_check:
            autoconnect_others_to(node, player, state)
            _hash = state_hash(state)
            score = -negamax(opponent_of(player), state, depth-1, -beta, -alpha, transpositions, depth)
            nodes_searched += 1
            transpositions[_hash % NUMBER_TRANSPOSITIONS] = (_hash, depth, score)
            disconnect_others_from(node, player, state)
            alpha = max(alpha, score)
            if score > best_score:
                best_node, best_score = node, score
            if alpha >= beta:
                break
    sys.stdout.write(cPickle.dumps((best_node, best_score, nodes_searched)))
    sys.exit(0)
