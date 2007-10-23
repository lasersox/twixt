#!/usr/bin/env python
"""
This file houses the core game code. It does not contain a game driver, and
contains only a stub-implementation of a `Player` class. All of this is written
from the perspective of a server, so client classes must still be implemented.
"""

class TwixtError(Exception):
    pass

class NodeError(TwixtError):
    pass

class Node(object):
    """
    This class represents a single node.
    
    A node has 5 attributes:
        `x`         the x position of the node
        `y`         the y position of the node
        `reservee`  the player for whom this node is reserved. (i.e. end nodes)
        `owner`     the owner of this node.
        `connected_nodes`
                    the *set* of nodes to which this node is connected.
    """
    # there should never be more than ONE Node object for a particular
    # combination of x,y.  Furthermore, these should be generated at the start
    # of each game!
    def __init__(self, x, y):
        """ `x` and `y` are the obvious arguments. """
        self.x = x
        self.y = y
        self.reservee = ""  # if the node is reserved this will be
                              # a reference to the eventual owner.
        self.owner = ""     # the node's reference to its owner.
        self.connected_nodes = set() # node's reference to adjacent nodes.
                                    # ie. nodes to which this node is
                                    # connected
    def __hash__(self):
      return hash((self.x, self.y, self.owner, self.connected_nodes))

class Connection(object):
    """
    This is a little throwaway class to make it easier for us to decide
    when a connection will be blocked.
    """
    # slots is for performance optimization, not for typing.
    __slots__ = ['p0', 'p1', 'domain', 'slope', 'intercept']
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        # domain is a 2-tuple.  each connection is defined only on it's 
        # "domain", that is, the space between it's leftmost and rightmost
        # node.
        self.domain = tuple(sorted([p0.x, p1.x]))
        # the euclidean slope of the connection
        self.slope = float(p1.y - p0.y) / float(p1.x - p0.x)
        # y-intercept.
        self.intercept = float(p0.y - self.slope * p0.x)
    

def intersects(conn0, conn1):
    """
    True if conn0 intersects conn1 on the domains of each of the two lines. (The
    domain of the line is the region of the x-axis between the two endpoints of
    the line).
    """
    # this function solves two bounded lines for the point of intersection.
    # if (x,y) is in the domain of both of the lines this function return true.
    if conn0.slope != conn1.slope: # check for parallelism.
        dm = float(conn0.slope - conn1.slope)
        db = float(conn0.intercept - conn1.intercept)
        ix = -db/dm # solving for x
        iy = conn0.slope*ix + conn0.intercept # solving for y.
        # now we have the point of interception but is it on the domain
        # of **both** lines?
        if conn0.domain[0] < ix and conn0.domain[1] > ix\
        and conn1.domain[0] < ix and conn1.domain[1] > ix:
            # the point of intersection is on the domain of both lines.
            return True
    # slopes are equal, or the point of intersection is not on the domain
    # of both lines.
    return False


class Twixt(object):
    """
    The Twixt class maintains game state.
    
    The Twixt class should not maintain the turn state. Turn state is managed by
    the game driver.
    """
    def __init__(self, player1, player2, size=(24,24)):
        """
        `player1` and `player2` can be any unique object.  Strings are
        generally ok.
        """
        self.player1 = player1
        self.player2 = player2
        self.size = size
        self.nodes = {}
        # set up all nodes.
        # notice: coords is a "generator comprehension".  this is like a 
        # list comprehension except that each element is only created as it
        # is requrested in the for loop.
        coords = ((x,y) for y in range(0, size[0]) for x in range(0, size[1]))
        for x, y in coords:
            # skip the corners.
            if x in [0, size[0]-1] and y in [0, size[1]-1]:
                continue
            self.nodes[x,y] = Node(x,y)
            # set up reserved nodes.
            if x in [0, size[0]-1]:
                self.nodes[x,y].reservee = player1
            elif y in [0, size[1]-1]:
                self.nodes[x,y].reservee = player2

    def __hash__(self):
      return hash(self.nodes)
    
    def claim_node(self, (x,y), player):
        """ Give ownership of the node at `(x,y)` to `player`. """
        if not self.nodes[x,y].owner:
            raise NodeError("The node at x,y is already owned.")
        if not self.nodes[x,y].reservee in [player, ""]:
            raise NodeError("This node is reserved.")
        self.nodes[x,y].owner = player
        
    def connect(self, (x0,y0), (x1,y1), player):
        """
        Connect node at `(x0,y0)` to node at `(x1,y1)` (and vice versa).
        
        This method will raise a `NodeError` if the two nodes are not
        connectable. Two nodes are "connectable" if the following hold
        true:
            1. Both nodes have the same owner.
            2. Nodes are a knight's move apart.
            3. There is no connection from two other nodes which would
               cross the new connection.
        """
        node0 = self.nodes[x0,y0]
        node1 = self.nodes[x1,y1]
        if not (player is node0.owner and player is node1.owner):
            raise NodeError("Player does not own both nodes.")
        xdif, ydif = abs(node0.x - node1.x), abs(node0.y - node1.y)
        if (xdif != 1 or ydif != 2) and (ydif != 1 or xdif != 2):
            raise NodeError("Nodes are not a knight's move apart.")
        conn = Connection(node0, node1)
        for other_conn in self.connections:
            if intersects(conn, other_conn):
                raise NodeError("Connection would be intersected by " \
                                "another connection.")
        node0.connected_nodes.add(node1)
        node1.connected_nodes.add(node0)
    
    def disconnect(self, (x0,y0), (x1,y1), player):
        """ Disconnect node at `(x0,y0)` from node at `(x1,y1)` """
        node0 = self.nodes[x0,y0]
        node1 = self.nodes[x1,y1]
        if not (player is node0.owner is node1.owner):
            raise NodeError("Player does not own both nodes.")
        if not (node0 in node1.connected_nodes and \
                node1 in node0.connected_nodes):
            raise NodeError("%s is not connected to %s." % (node0, node1))
        node0.connected_nodes.remove(node1)
        node1.connected_nodes.remove(node0)
     
    def starting_nodes(self, player):
        """ Iterates over the *owned* starting nodes of `player`. """
        return self._owned_nodes(player, 'start')
    
    def finishing_nodes(self, player):
        """ Iterates over the *owned* finishing nodes of `player`. """
        return self._owned_nodes(player, 'finish')
    
    def _owned_nodes(self, player, area):
        """
        Iterates over the nodes owned by `player` at `area` where `area`
        is either 'start' or 'finish'.
        """
        if area == "start":
            m = 0
        elif area == "finish":
            if player is self.player1:
                side = 0
            elif player is self.player2:
                side = 1
            m = self.size[side]-1
        if player is self.player1:
            node = lambda n: m, n
        elif player is self.player2:
            node = lambda n: n, m
        for n in range(1,self.size[not side]-1):
            if self.nodes[node(n)].owner is player:
                yield self.nodes[node(n)]
    
    @property
    def connections(self):
        for node in self.nodes.itervalues():
            for other_node in node.connected_nodes:
                yield Connection(node, other_node)
    
    def has_won(self, player):
        """ Performs node search to see if `player` has won. """
        marked = set()
        stack = []
        # perform search
        for node in self.starting_nodes(player):
            marked.add(node)
            stack.append(node)
        while len(stack):
            current_node = stack.pop()
            for node in current_node.connected_nodes:
                if node in self.finishing_nodes(player):
                    return True
                if not node in marked:
                    marked.add(node)
                    stack.append(node)
        return False
    
