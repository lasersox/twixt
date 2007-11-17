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

	for node0 in game.nodes
		if node0.owner == player.name
			for node1 in game.nodes
				if node1.owner = "" and node1.reservee != game.opponent(player).name
					xdif, ydif = abs(node0.x - node1.x), abs(node0.y - node1.y)
					if !((xdif != 1 or ydif != 2) and (ydif != 1 or xdif != 2)):						
						""" check for intersection """
						conn = Connection(node0, node1)
						for other_conn in self.connections:
							if !intersects(conn, other_conn):
								ext_bridges += 1
	
	return ext_bridges		
	
	
def get_next_states(game,player,depth)
	""" generate all possible game states at depth ahead 
	1. Notice, make sure return (game,node) """
	pass

