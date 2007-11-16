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
	pass

def f_5(game, player):
	pass

def f_6(game, player):
	return 1 / f_4(game, game.player)

def f_7(game, player):
	pass

def f_8(game, player):
	pass

