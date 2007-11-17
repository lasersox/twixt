from math import *

def f_1(game, player):
    """ Compute total length of bridges for player. """
    conn_len = sqrt(1 + 2.**2)
    total = 0
    for conn in game.connections:
        if conn.p0.owner == player and conn.p1.owner == player:
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
    return max(conn_bridges)/(game.size[0]*game.size[1])

def f_4(game, player):
    """ looping through all the bridges and project it to the vertical axis """
    distance = 0
    vnodes = [0]*game.size[0]
    bridges = game.connections(player)
    
    for bridge in bridges:
        vnodes[bridge.p0.y] = 1
        vnodes[bridge.p1.y] = 1
        vnodes[round((bridge.p0.y + bridge.p1.y)/2)] = 1
    
    return sum(vnodes)/(game.size[0]*game.size[1])


def f_5(game, player):
    """ looping through all the bridges and project it to the vertical axis """
    distance = 0
    hnodes = [0]*game.size[1]
    bridges = game.connections(player)
    
    for bridge in bridges:
        hnodes[bridge.p0.x] = 1
        hnodes[bridge.p1.x] = 1
        hnodes[round((bridge.p0.x + bridge.p1.x)/2)] = 1
    
    return sum(hnodes)/(game.size[0]*game.size[1])


def f_6(game, player):
    """ Return the reciprocal of player's f_4. """
    return 1 / f_4(game, player)

def f_7(game, player):
    """ Return the reciprocal of player's f_5. """
    return 1 / f_5(game, player)

def f_8(game, player):
    """ Evaluate the ability to extend the current bridges """
    ext_bridges = 0

    for node0 in game.nodes:
            if node0.owner == player.name:
                for node1 in game.nodes:
                    if node1.owner == "" and node1.reservee != game.opponent(player).name:
                        xdif, ydif = abs(node0.x - node1.x), abs(node0.y - node1.y)
                        if ((xdif != 1 or ydif != 2) and (ydif != 1 or xdif != 2))== False:                     
                            """ check for intersection """
                            conn = Connection(node0, node1)
                            for other_conn in self.connections:
                                if intersects(conn, other_conn) == False:
                                    ext_bridges += 1
        
    return ext_bridges      
    
    
def get_next_states(game,player,depth):
    """ generate all possible game states at depth ahead 
    1. Notice, make sure return (game,node) 
    Comment: Using array to store the tree: A node will be an array of [[Current],[Childrent],[Move]]"""
    parrent = [game,[], []]
    parrent = get_next_recur_states(parrent, player, depth)
    return parrent      

def get_next_recur_states(parrent, player, depth):
    """ Using recursion to generate next states recursively 
    Note: a node is [game, chidren, move]"""
    
    # get all the valid nodes for this player
    valid_nodes = get_valid_nodes(parrent[0],player)
        
    # This is the leaf node
    if depth == 1:  
        for valid_node in valid_nodes:
            # get a copy the current game board
            temp_game = parrent[0]
            # claim the avalaible node
            temp_game.claim_node((valid_node.x, valid_node.y),player)
            # add the new game board to as the child to the current node
            parrent[1].append([temp_game,[],valid_node])    
    else: #if not leaf, call recursively
        for valid_node in valid_nodes:
            # determine which player is in turn
            if depth%2 == 0:
                cur_player = parrent[0].opponent(player)
                
            temp_states = get_next_recur_states(parrent,cur_player,depth-1)
            for temp_state in temp_states:
                parrent[1].append(temp_state) 
    
    return parrent

def get_next_loo_states(parrent, player, depth):
    for i in range(depth):
       
       pass
        
def get_valid_nodes(game,player):
    """ return the valid nodes for a player """
    valid_nodes = set()
    for node in game.nodes.itervalues():
        if node.owner == "" or node.reservee == player:
            valid_nodes.add(node)
    return valid_nodes
 
    

