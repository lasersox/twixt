from math import *
from pytwixt import node_twixt as twixt
import copy

def f_1(game, player):
    """ Compute total length of bridges for player. """
    conn_len = sqrt(1 + 2.**2)
    total = 0
    for conn in game.connections(player):
            total += conn_len
    return total / (game.size[0] * game.size[1])

def f_2(game, player):
    """ Return the difference between player's f_1 and the opponent's f_1. """
    return f_1(game, player) - f_1(game, game.player2)

def f_3(game, player):
    """ checking for longest bridge """
    bridges = list(game.connections(player))
    conn_bridges = set()
    
    for bridge in bridges:
        conn_nodes = set()
        conn_nodes.add(bridge.p0)
        conn_nodes.add(bridge.p1)
        bridges.remove(bridge)
         
        for bridge1 in bridges:
            if bridge1.p0 in conn_nodes:
                conn_nodes.add(bridge.p1)
                bridges.remove(bridge1)
                
            if bridge1.p1 in conn_nodes:
                conn_nodes.add(bridge.p0)
                bridges.remove(bridge1)
                
        conn_bridges.add(len(conn_nodes)-1)
        
    """ checking for longest path """
    if not conn_bridges:
        return 0
    return max(conn_bridges)/(game.size[0]*game.size[1])

def f_4(game, player):
    """ looping through all the bridges and project it to the vertical axis """
    distance = 0
    vnodes = [0]*game.size[0]
    bridges = game.connections(player)
    
    for bridge in bridges:
        vnodes[bridge.p0.y] = 1
        vnodes[bridge.p1.y] = 1
        vnodes[int(round((bridge.p0.y + bridge.p1.y)/2))] = 1
    
    return float(sum(vnodes)/(game.size[0]*game.size[1]))


def f_5(game, player):
    """ looping through all the bridges and project it to the vertical axis """
    distance = 0
    hnodes = [0]*game.size[1]
    bridges = game.connections(player)
    
    for bridge in bridges:
        hnodes[bridge.p0.x] = 1
        hnodes[bridge.p1.x] = 1
        hnodes[int(round((bridge.p0.x + bridge.p1.x)/2))] = 1
    
    return float(sum(hnodes)/(game.size[0]*game.size[1]))


def f_6(game, player):
    """ Return the reciprocal of player's f_4. """
    return 1. / (f_4(game, player)+1)

def f_7(game, player):
    """ Return the reciprocal of player's f_5. """
    return 1. / (f_5(game, player) + 1)

def f_8(game, player):
    """ Evaluate the ability to extend the current bridges """
    ext_bridges = 0

    for node0 in game.nodes.itervalues():
        if node0.owner == player.name:
            for node1 in game.nodes.itervalues():
                if node1.owner == "" and node1.reservee != game.opponent(player):
                    xdif, ydif = abs(node0.x - node1.x), abs(node0.y - node1.y)
                    if ((xdif != 1 or ydif != 2) and (ydif != 1 or xdif != 2))== False:                     
                        """ check for intersection """
                        conn = twixt.Connection(node0, node1)
                        for other_conn in game.connections(game.opponent(player)):
                            if twixt.intersects(conn, other_conn) == False:
                                ext_bridges += 1
    return ext_bridges      
    
    
def get_next_states(game,player,depth):
    """ generate all possible game states at depth ahead 
    1. Notice, make sure return (game,node) 
    Comment: Using array to store the tree: A node will be an array of [[Current],[Childrent],Move, score]"""
    parent = [game, [], None, None]
    parent = get_next_recur_states(parent, player, depth)
    return parent      

def get_next_recur_states(parent, player, depth):
    """ Using recursion to generate next states recursively 
    Note: a node is [game, chidren, move]"""
    
    # get all the valid nodes for this player
    # This is the leaf node
    if depth == 1:  
        valid_nodes = get_valid_nodes(parent[0],player)
        for valid_node in valid_nodes:
            # get a copy the current game board
            temp_game = copy.deepcopy(parent[0])
            # claim the avalaible node
            try:
                temp_game.claim_node((valid_node.x, valid_node.y), player)
            except twixt.NodeError, e:
                print player, valid_node.reservee
                raise e
            # add the new game board to as the child to the current node
            parent[1].append([temp_game,[],valid_node])    
    else: #if not leaf, call recursively
        # determine which player is in turn
        valid_nodes = get_valid_nodes(parent[0], player)
        for valid_node in valid_nodes:
            # get a copy the current game board
            temp_game = copy.deepcopy(parent[0])
            # claim the avalaible node
            try:
                temp_game.claim_node((valid_node.x, valid_node.y), player)
            except twixt.NodeError, e:
                print player, valid_node.reservee
                raise e
            temp_states = get_next_recur_states([temp_game, [], valid_node], parent[0].opponent(player), depth-1)
            parent[1].append(temp_states) 
    return parent

def get_next_loo_states(parent, player, depth):
    for i in range(depth):
       
       pass
        
def get_valid_nodes(game,player):
    """ return the valid nodes for a player """
    valid_nodes = set()
    for node in game.nodes.itervalues():
        if node.reservee == game.opponent(player):
            continue
        if node.owner == "" and node.reservee != game.opponent(player):
            valid_nodes.add(node)
    return valid_nodes



