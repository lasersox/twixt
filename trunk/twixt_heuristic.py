from math import *
from pytwixt import node_twixt as twixt
import copy
import sys

def f_1(game, player):
    """ Compute total length of bridges for player. """
    conn_len = sqrt(1 + 2.**2)
    total = 0
    for conn in game.connections(player):
            total += conn_len
    return total / (game.size[0] * game.size[1])

def f_2(game, player):
    """ Return the difference between player's f_1 and the opponent's f_1. """
    return f_1(game, player) - f_1(game, game.opponent(player))

def f_3(game, player):
     """ checking for longest bridge """
     bridges = list(game.connections(player))
     #print len(bridges)
     conn_bridges = []
 
     #print " bridges %s %s " % (bridges, len(bridges))
     conn_len = len(bridges)
     while conn_len != 0:
         bridge = bridges[0]
         #print " bridge %s %s " % (bridge.p0,bridge.p1)
         conn_nodes = []
         conn_nodes.append(bridge.p0)
         conn_nodes.append(bridge.p1)
         bridges.remove(bridge)
         #print "bridge length : %s "  % len(conn_nodes)
         # merging here
         for conn_bridge in conn_bridges:
             if bridge.p0 in conn_bridge:
                 conn_bridge.append(bridge.p1)
                 
             elif bridge1.p1 in conn_bridge:
                 conn_bridge.append(bridge1.p0)
                 bridges.remove(bridge1)
                
         for bridge1 in bridges:
             #print " bridge1 %s %s " % (bridge1.p0,bridge1.p1)
             if bridge1.p0 in conn_nodes:
                 conn_nodes.append(bridge1.p1)
                 bridges.remove(bridge1)
                 
             elif bridge1.p1 in conn_nodes:
                 conn_nodes.append(bridge1.p0)
                 bridges.remove(bridge1)
         
                 
             #print "bridge length : %s "  % len(conn_nodes)
                 
         conn_bridges.append(conn_nodes)
         conn_len = len(bridges)
        
   
     #print "bridge length : %s "  % conn_bridges
     """ checking for longest path """
     if not conn_bridges:
         return 0
     return  max(conn_bridges) #float(float(max(conn_bridges))/(game.size[0]*game.size[1]))

# def f_3(game, player):
# 
#     max_len = 0
#     marked = set()
#     
#     # perform search
#     for node in self.claimed_nodes(player):
#         if node in marked: continue
#         marked.add(node)
#         temp_len = 0
#         stack = set()
#         stack.union(node.connected_nodes)
#         while len(stack):
#             node = stack.pop()
#             for other_node in node.connected_nodes:
#                 
#                 stack.append(other_node)
#     return False



def f_4(game, player):
    """ looping through all the bridges and project it to the goal axis """
    if game.player1 == player:
        edge = lambda node: node.x
        axis = 0
    else:
        edge = lambda node: node.y
        axis = 1
    
    distance = 0
    vnodes = [0]*game.size[axis]
    bridges = game.connections(player)
    
    for bridge in bridges:
        vnodes[edge(bridge.p0)] = 1
        vnodes[edge(bridge.p1)] = 1
        vnodes[(edge(bridge.p0) + edge(bridge.p1))/2] = 1
    
    return float(float(sum(vnodes))/float(game.size[axis]))


def f_5(game, player):
    """ looping through all the bridges and project it to the opponent's goal axis """
    
    if game.player1 == player:
        edge = lambda node: node.y
        axis = 1
    else:
        edge = lambda node: node.x
        axis = 0
    
    distance = 0
    hnodes = [0]*game.size[axis]
    bridges = game.connections(player)
    
    for bridge in bridges:
        hnodes[edge(bridge.p0)] = 1
        hnodes[edge(bridge.p1)] = 1
        hnodes[(edge(bridge.p0) + edge(bridge.p1))/2] = 1
    
    return 1. - float(sum(hnodes))/game.size[axis]


def f_6(game, player):
    """ Return the reciprocal of player's f_4. """
    return 1. / (f_4(game, player)+1)

def f_7(game, player):
    """ Return the reciprocal of player's f_5. """
    return 1. / (f_5(game, player) + 1)

def f_8(game, player):
    """ Evaluate the ability to extend the current bridges """
    ext_bridges = 0

    """***** by Lan *****"""
    connected_nodes = len(list(game.nodes.itervalues()))
    
    for node0 in game.nodes.itervalues():
        """***** by Lan *****"""
        #if node0.owner == player IS REPLACED BY:
        if node0.owner == player and len(node0.connected_nodes) != 0:
            for node1 in game.nodes.itervalues():
                if node1.owner == "" and node1.reservee != game.opponent(player):
                    xdif, ydif = abs(node0.x - node1.x), abs(node0.y - node1.y)
                    if ((xdif != 1 or ydif != 2) and (ydif != 1 or xdif != 2))== False:                     
                        """ check for intersection """
                        conn = twixt.Connection(node0, node1)
                        for other_conn in game.connections(game.opponent(player)):
                            if twixt.intersects(conn, other_conn) == False:
                                ext_bridges += 1
    """***** by Lan *****"""
    #return float(float(4*ext_bridges)/(game.size[0]*game.size[1]))
    return float(float(ext_bridges)/connected_nodes)    

def f_9(game, player):
    """ Evaluate ability to win 
    The player should choose a move leading to a win without considering
    other heuristics - return +inf basically """
    
    if game.has_won(player):
        return sys.maxint
    else:    
        return 0

    
def f_10(game, player):
    """ Evaluate possibility to lose
    The player should choose a move that is not leading to a loose. In other words,
    If the player is in loosing situation, he should prevent the opponent from winning
    Need to consider : maybe covered in the Minmax search already
    """
    if game.has_won(game.opponent(player)):
        return -sys.maxint/2
    else:    
        return 0

def g_1(game, player):
    return (f_4(game, player) - f_4(game, game.opponent(player))) / game.size[0]
    

def get_next_states(game, depth):
    """ generate all possible game states at depth ahead 
    1. Notice, make sure return (game,node) 
    Comment: Using array to store the tree: A node will be an array of [[Current],[Childrent],Move, score]"""
    parent = [game, [], None]
    #print "calling get_next_recur_states with (%s, %s)." % (parent, depth)
    parent = get_next_recur_states(parent, depth)
    return parent      

def get_next_recur_states(parent, depth):
    """ Using recursion to generate next states recursively 
    Note: a node is [game, chidren, move]"""
    
    # get all the valid nodes for this player
    # This is the leaf node
    if depth == 1:  
        valid_nodes = get_valid_nodes(parent[0])
        #print "Current_player: " + parent[0].current_player
        #for node in valid_nodes: print "  " + node.reservee + " %i, %i" % (node.x, node.y)
        for valid_node in valid_nodes:
            # get a copy the current game board
            temp_game = copy.deepcopy(parent[0])
            # claim the avalaible node
            try:
                temp_game.claim_node((valid_node.x, valid_node.y), temp_game.current_player)
                temp_game.current_player = temp_game.opponent(temp_game.current_player)
            except twixt.NodeError, e:
                print player, valid_node.reservee
                raise e
            # add the new game board to as the child to the current node
            parent[1].append([temp_game,[],valid_node])    
    else: #if not leaf, call recursively
        # determine which player is in turn
        valid_nodes = get_valid_nodes(parent[0])
        for valid_node in valid_nodes:
            # get a copy the current game board
            temp_game = copy.deepcopy(parent[0])
            # claim the avalaible node
            try:
                temp_game.claim_node((valid_node.x, valid_node.y), temp_game.current_player)
                temp_game.current_player = temp_game.opponent(temp_game.current_player)
            except twixt.NodeError, e:
                print player, valid_node.reservee
                raise e
            temp_states = get_next_recur_states([temp_game, [], valid_node], depth-1)
            parent[1].append(temp_states) 
    return parent

def get_valid_nodes(game):
    """ return the valid nodes for a player """
    valid_nodes = set()
    for node in game.nodes.itervalues():
        if node.owner == "" and node.reservee in [game.current_player, ""]:
            valid_nodes.add(node)
    return valid_nodes



