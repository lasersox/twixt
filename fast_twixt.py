import copy
import random

width, height = 8, 8
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

root_state = {"p1" : {"nodes": set(), "connections": {}},
              "p2" : {"nodes": set(), "connections": {}}}

def state_hash(state):
    return hash(tuple([
        tuple(sorted(state['p1']['nodes'])),
        tuple(sorted(state['p2']['nodes'])),
        tuple(sorted(tuple([node, tuple(sorted(connected_nodes))]) for node, connected_nodes in state['p1']['connections'].iteritems())),
        tuple(sorted(tuple([node, tuple(sorted(connected_nodes))]) for node, connected_nodes in state['p2']['connections'].iteritems()))
    ]))

def claim(node, player, state):
    state[player]['nodes'].add(node)
    autoconnect_others_to(node, player, state)
    
def opponent_of(player): return 'p1' if player == 'p2' else 'p2'

def the_winner_is(player, state):
    _starting_nodes  =  starting_nodes[player].intersection(state[player]["nodes"])
    _finishing_nodes = finishing_nodes[player].intersection(state[player]["nodes"])
    _connections     = state[player]["connections"]
    
    marked = set()
    stack = []
    
    # perform search
    for node in _starting_nodes:
        marked.add(node)
        stack.append(node)
    while len(stack):
        current_node = stack.pop()
        if current_node not in _connections: continue
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
    t = game_nodes.difference(state['p1']['nodes'].union(state['p2']['nodes']).union(reserved_nodes['p1']).union(reserved_nodes['p2']))
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
    if player == "p1":
        project = lambda node: node[0]
        axis = width
    elif player == "p2":
        project = lambda node: node[1]
        axis = height

    projection = [0] * axis
    
    _connections = state[player]["connections"]
    
    longest_length = 0
    marked = set()
    
    for node in state[player]['nodes']:
        if node in marked or node not in _connections: continue
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
            longest_length = path_length + 1
    return longest_length
    
def heuristic_value_of(state):
    return zeta('p1', state) - zeta('p2', state) + random.random() / 4.

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
    other_player = opponent_of(player)
    potential_blockers = set((node[0]+dx, node[1]+dy) for (dx,dy) in __autoconnect_differentials)
    potential_blockers.update(set((other_node[0]+dx, other_node[1]+dy) for (dx,dy) in __autoconnect_differentials))
    potential_blockers.intersection_update(state[other_player]['nodes'])
    while len(potential_blockers):
        blocker = potential_blockers.pop()
        if blocker not in state[other_player]['connections']: continue
        for other_blocker in state[other_player]['connections'][blocker]:
            if intersects([node, other_node], [blocker, other_blocker]):
                return False
    # make the connection
    if node not in state[player]['connections']:
        state[player]['connections'][node] = []
    if other_node not in state[player]['connections']:
        state[player]['connections'][other_node] = []
    state[player]['connections'][node].append(other_node)
    state[player]['connections'][other_node].append(node)
    return True
        
def autoconnect_others_to(node, player, state):
    # autoconnect all other possilbe nodes to node.
    number_connected = 0
    for dx,dy in __autoconnect_differentials:
        other_node = (node[0]+dx, node[1]+dy)
        if not other_node in state[player]['nodes']: continue
        if attempt_to_connect(other_node, node, player, state):
            number_connected += 1
    return number_connected

def disconnect_others_from(node, player, state):
    if node not in state[player]['connections']:
        return
    for other_node in state[player]['connections'][node]:
        state[player]['connections'][other_node].remove(node)
        if not state[player]['connections'][other_node]:
            del state[player]['connections'][other_node]
    del state[player]['connections'][node]

def available_nodes(player, state):
    
    available_nodes = game_nodes \
                        .difference(state['p1']['nodes']) \
                        .difference(state['p2']['nodes']) \
                        .difference(reserved_nodes[opponent_of(player)])
    for node in available_nodes:
        yield node
        
def negamax(state, depth, alpha, beta, explored=set()):
    player = 'p1' if len(state['p1']['nodes']) == len(state['p2']['nodes']) else 'p2'
    if is_terminal(state) or depth == 0:
        return heuristic_value_of(state)
    else:
        for node in available_nodes(player, state):
            state[player]['nodes'].add(node)
            autoconnect_others_to(node, player, state)
            if state_hash(state) in explored:
                disconnect_others_from(node, player, state)
                state[player]['nodes'].remove(node)
                continue
            explored.add(state_hash(state))
            score = -negamax(state, depth-1, -beta, -alpha, explored)
            disconnect_others_from(node, player, state)
            state[player]['nodes'].remove(node)
            alpha = max(alpha, score)
            if alpha >= beta:
                return beta
        return alpha

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