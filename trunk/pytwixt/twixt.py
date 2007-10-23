#!/usr/local/bin/python

import math
from itertools import chain

class TwixtError(Exception):
    pass

class BridgeError(TwixtError):
    pass

class PegError(TwixtError):
    pass


class Peg(tuple):
    def __init__(self, (y,x)):
        """x is the x coordinate of this peg, y is the y coordinate 
        of this peg. adjacent_pegs is a dictionary of the pegs connected
        to this peg via bridges."""
        tuple.__init__(self, (x,y))
        self.adjacent_pegs = set()
    
    def __repr__(self):
        return "Peg(%s,%s)" % (self.x, self.y)
    
    def __getattr__(self, key):
        if key == "x":
            return self[0]
        elif key == "y":
            return self[1]
        raise AttributeError
    
    def has_bridges(self):
        """True if peg is connected to ANY peg by a bridge;
        False otherwise.
        """
        print self.adjacent_pegs
        return bool(self.adjacent_pegs)
    
    def is_connected_to(self, p):
        """Returns true if self is connected to Peg p via a bridge;
        returns false otherwise.
        """
        print self.adjacent_pegs
        return p in self.adjacent_pegs
    
    def connect_to(self, p):
        """Connects self to the Peg p."""
        self.adjacent_pegs = self.adjacent_pegs.union(set(p))
        print "connecting"
        print self.adjacent_pegs
    
    def disconnect_from(self, p):
        """Disconnects self from Peg p."""
        return self.adjacent_pegs.discard(p)
    

class Bridge(tuple):
    def __init__(self, (p1, p2)):
        """p1 is one of the Pegs this bridge connects
        p2 is the other Peg this bridge connects.
        """
        # Make sure pins are a knight's move apart.
        xdif, ydif = abs(self.p1.x - self.p2.x), abs(self.p1.y - self.p2.y)
        if (xdif == 1 and ydif == 2) or (ydif == 1 and xdif == 2):
            #raise BridgeError  ##line removed for interface
            return False
        tuple.__init__(self, (self.p1, self.p2))
    
    def __getattr__(self, key):
        if key == "p1":
            return self[0]
        elif key == "p2":
            return self[1]
        raise AttributeError
    
    def __repr__(self):
        return "Bridge(%s,%s)" % (self.p1, self.p2)
    
    def _left_peg(self):
        if self.p1.x < self.p2.x:
            return self.p1
        else:
            return self.p2
    left_peg = property(fget=_left_peg,
                    doc="Returns the leftmost Peg associated with this Bridge")
    
    def _right_peg(self):
        if self.p1.x < self.p2.x:
            return self.p2
        else:
            return self.p1
    right_peg = property(fget=_right_peg,
                doc="Returns the rightmost Peg associated with this Bridge.")
    
    def _top_peg(self):
        if self.p1.y < self.p2.y:
            return self.p2
        else:
            return self.p1
    top_peg = property(fget=_top_peg,
                        doc="The topmost Peg associated with this Bridge.")
    
    def _bottom_peg(self):
        if self.p1.y < self.p2.y:
            return self.p1
        else:
            return self.p2
    bottom_peg = property(fget=_bottom_peg,
                         doc="The bottom-most Peg associated with this Bridge.")
    
    def _slope(self):
        return float(self.p2.y - self.p1.y) / float(self.p2.x - self.p1.x)
    slope = property(fget=_slope,
                      doc="the slope of the line through the two pegs.")
    
    def _intercept(self):
        return float(self.p1.y - self.slope() * self.p1.x)
    intercept = property(fget=_intercept,
                          doc="Returns the y-intercept of the slope "\
                              "of the line through the two pegs.")
    
    def is_horizontal(self):
        """Returns true for horizontal bridge; false for vertical."""
        if self.top_peg.y - self.bottom_peg.y == 1:
            return True
        return False
    
    def near_pegs(self):
        """Returns a generator for pegs that could possibly be part
        of a blocking bridge."""
        nearpegs = []
        if self.is_horizontal():
            if self.left_peg is self.top_peg:
                left, right = self.top_peg, self.bottom_peg
            else:
                right, left = self.top_peg, self.bottom_peg
            print left
            print right
            for x in range(left.x+1, left.x+4):
                nearpegs.append(Peg((x, left.y)))
            for x in range(right.x-3, right.x):
                nearpegs.append(Peg((x, right.y)))
#            leftside = (Peg([left.y, x]) for x in range(left.x+1, left.x+4))
#            rightside = (Peg([right.y, x]) for x in range(right.x-3, right.x))
#            one, two = leftside, rightside
        else:
            if self.left_peg is self.top_peg:
                top, bottom = self.left_peg, self.right_peg
            else:
                bottom, top = self.right_peg, self.left_peg
            for y in range(top.y+1, top.y+4):
                nearpegs.append(Peg((top.x, y)))
            for y in range(bottom.y-3, bottom.y):
                nearpegs.append(Peg((bottom.x, y)))
            """
            topside = (Peg([y, top.x]) for y in range(top.y+1, top.y+4))
            botside = (Peg([y, bottom.x]) for y in range(bottom.y-3, bottom.y))
            one, two = topside, botside
            """
#        print chain(one, two)
#        return chain(one, two)
        return nearpegs
    
    def intersects(self, other):
        """True if self intersects other."""
        # if slopes are equal intersection is impossible
        print self.slope
        print other.slope
        if not self.slope == other.slope:
            print self.slope
            print other.slope
            dm = float(self.slope - other.slope)
            print dm
            db = float(self.intercept - other.intercept)
            print db
            ix = -db/dm # point of interception
            print ix
            # solving one equation for y
            iy = self.slope*ix + self.intercept
            print iy
            # if point of intersection is on the bridge.
            if other.left_peg.x < ix and other.right_peg.x > ix\
                        and other.top_peg.y > iy and other.bottom_peg.y < iy:
                return True
            else: return False
        return False
    

class Player:
    """
    dir_ is either 'x' or 'y', indicating which dir_tion the player builds
    
    pegs is a dictionary of the pegs owned by this player
    start_pegs is a list of pegs in the start row (determined by dir_) owned
      by this player (used for the search to determine the end of the
      game)
    bridges is a dictionary of the bridges owned by this player.
    color is the color of this player"""
    
    def __init__(self, name, dir_, color=(0,0,0)):
        self.dir_ = dir_
        self.name = name
        self.pegs = {}
        self.start_pegs = {}
        self.bridges = {}
        self.color = color
    
    def insert_peg(self, peg):
        """Creates a new Peg at coordinates (x,y) owned by this player."""
        if peg:
            self.pegs[peg] = peg
            if self.dir_ == 'x' and peg.x == 0\
                    or self.dir_ == 'y' and peg.y == 0:
                self.start_pegs[peg] = peg
            return True
        return False
    
    def insert_bridge(self, bridge):
        """Creates a new Bridge connecting Pegs p1 and p2 owned
        by this player."""
        xdif = abs(bridge.p1.x - bridge.p2.x)
        ydif = abs(bridge.p1.y - bridge.p2.y)
        if (xdif == 1 and ydif == 2) or (xdif == 2 and ydif == 1):
            if bridge.p1 in self.pegs and bridge.p2 in self.pegs:
                self.bridges[bridge] = bridge
                bridge.p1.connect_to(bridge.p2)
                bridge.p2.connect_to(bridge.p1)
                return True
        return False
    
    def remove_bridge(self, bridge):
        """Removes a Bridge owned by this player."""
        if bridge in self.bridges:
            del self.bridges[bridge]
            bridge.p1.disconnect_from(bridge.p2)
            bridge.p2.disconnect_from(bridge.p1)
            return True
        return False

    

class Twixt:
    """
    size is the number of dots on the board, not including goal zones
    player1 is a Player.
    player2 is the other Player.
    curplayer is the player whose turn it is
    phase is the current phase of the turn
        0 is remove bridges
        1 is place peg
        2 is place bridges
    """
    
    def __init__(self, player1, player2, size=24):
        self.player1 = player1
        self.player2 = player2
        self.size = size
        self.curplayer = self.player2
        self.phase = 0
    
    def remove_bridge(self, bridge, player=None):
        "Removes Bridge bridge from Player player."
        if bridge.p2.x < bridge.p1.x:
            return self.remove_bridge(Bridge((bridge.p2, bridge.p1)), player)
        if player == None:
            player = self.curplayer
        if bridge:
            return player.remove_bridge(bridge)
        return False
    
    def insert_peg(self, peg, player=None):
        """Inserts a Peg for Player player at coordinates (x, y)
        if no Peg already exists there."""
        if player == None:
            player = self.curplayer
        if peg != None:
            if not peg in self.player1.pegs and not peg in self.player2.pegs:
                player.insert_peg(peg)
                return True
        return False
    
    def insert_bridge(self, bridge, player=None):
        """Inserts a Bridge for Player player between Pegs p1 and p2,
        if no Bridge would cross its path."""
        if bridge.p2.x < bridge.p1.x:
            return self.insert_bridge(Bridge((bridge.p2, bridge.p1)), player)
        if player == None:
            player = self.curplayer
        if bridge:
            print bridge
            if not self.blocked(bridge):
                return player.insert_bridge(bridge)
            else: return False
        return False
    
    def blocked(self, bridge):
        """Tests to see if a bridge will cross the bridge
        which spans Pegs p1 and p2."""
        print bridge.near_pegs()
        for peg in bridge.near_pegs():
            print peg
            if peg in self.player1.pegs:
                print "p1"
                peg = self.player1.pegs[peg]
            elif peg in self.player2.pegs:
                print "p2"
                peg = self.player2.pegs[peg]
            else:
                print "none"
                continue
            if peg.has_bridges():
                print "bridges"
                for other in peg.adjacent_pegs:
                    blocker = Bridge((peg, otherPeg))
                    print blocker
                    if bridge.intersects(blocker):
                        return True
        return False
    
    def swap_curplayer(self):
        if self.curplayer == self.player1:
            self.curplayer = self.player2
        else:
            self.curplayer = self.player1

    def next_phase(self):
        """Increments the phase of the turn and swaps the current player
        if a new turn has begun"""
        self.phase += 1
        self.phase %= 2
        if self.phase == 0:
            self.swap_curplayer()
            
    def is_goalpeg(self, peg, player):
        """Returns true if the given peg is in player's goal area,
        returns false otherwise."""
        if player.dir_ == 'x' and peg.x == size + 1 or\
         player.dir_ == 'y' and peg.y == size + 1:
            return True
        return False
    
    def has_won(self, player):
        """Performs search on pegs to see if player has won."""
        marked = set()
        stack = []
        # perform search
        for start_peg in player.start_pegs.itervalues():
            marked.add(start_peg)
            stack.append(start_peg)
        while len(stack):
            current = stack.pop()
            for peg in current.adjacent_pegs.itervalues():
                if self.is_goalpeg(peg, player):
                    return True
                if not peg in marked:
                    marked.add(peg)
                    stack.append(peg)
        return False
    
    def __repr__(self):
        return """%(player1)s
          Pegs:
           %(p1pegs)s
          Bridges:
           %(p1bridges)s
        %(player2)s
          Pegs:
           %(p2pegs)s
          Bridges:
           %(p2bridges)s
        """ % {"player1": self.player1.name,
               "player2": self.player2.name,
               "p1pegs": "\n".join(self.player1.pegs),
               "p2pegs": "\n".join(self.player2.pegs),
               "p1bridges": "\n".join(self.player1.bridges),
               "p2bridges": "\n".join(self.player2.bridges)}
    


if __name__ == "__main__":
    def safe_input(parser):
        while 1:
            try: return parser(raw_input("> "))
            except: pass
    # This is a simple text-based driver to the Twixt game class.
    print "*********************"
    print "* Welcome to Twixt. *"
    print "*********************"
    print 
    # get player 1
    print "Player 1, Enter your name:"
    name = raw_input("> ")
    p1 = Player(name, 'x', (255,0,0))
    # get player 2
    print "Player 2, Enter your name:"
    name = raw_input("> ")
    p2 = Player(name, 'y', (0,0,255))
    # init game
    g = Twixt(p1, p2)
    # game loop
    while 1:
        try:
            print g
            peg, burn, build = safe_input(parse_move)
            self.insert_peg(peg)
            for bridge in burn:
                g.remove_bridge(bridge)
            for bridge in build:
                g.insert_bridge(bridge)
            g.swap_curplayer()
        except PegError:
            print 'Invalid Peg'
            continue
        except BridgeError:
            print 'Invalid Bridge'
            continue
