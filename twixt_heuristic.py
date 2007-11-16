from math import *

def f_1(game, player):
	""" Compute total length of bridges for player. """
	conn_len = sqrt(1.**2 + 2.**2)
	total = 0
	for conn in game.connections:
		if conn.p0.owner == player and conn.p1.owner == player:
			total += conn_len
	return total / (game.size[0] * game.size[1])

def f_2(game, player):
	return f_1(game, player) - f_1(game, game.player2)

def f_3(game, player):
	pass

def f_4(game, player):
	""" looping through all the bridges and project it to the vertical axis """
	distance = 0
	vnodes = [0]*game.size
	bridges = game.connections(player)
	
	for bridge in bridges:
		vnodes[bridge.p0.y] = 1
		vnodes[bridge.p1.y] = 1
		vnodes[round((bridge.p0.y + bridge.p1.y)/2)] = 1
	
	return sum(vnodes)/(game.size*game.size)


def f_5(game, player):
	""" looping through all the bridges and project it to the vertical axis """
	distance = 0
	hnodes = [0]*game.size
	bridges = game.connections(player)
	
	for bridge in bridges:
		hnodes[bridge.p0.x] = 1
		hnodes[bridge.p1.x] = 1
		hnodes[round((bridge.p0.x + bridge.p1.x)/2)] = 1
	
	return sum(hnodes)/(game.size*game.size)


def f_6(game, player):
	return 1 / f_4(game, player)

def f_7(game, player):
	return 1 / f_5(game, player)

def f_8(game, player):
	pass
