"""
A server/game driver for `Twixt`.

The players may be on this machine, or not.
They may be computer-controlled, or not.
They may be playing via e-mail, a web browser, or by some other kind of client.
(Note, all of these clients may not be implemented...)
"""

"""
todo:
1. implement some sort of `broadcast` method, to keep both players of a game
   informed of the current game state.
2. Remove blocking loop in `create`.
"""
import sys, time, re
import SocketServer
import node_twixt as twixt

# the three turn phases.
CLAIM = 0
DISCONNECT = 1
CONNECT = 2

class ParseError(Exception):
    pass

def parse(node):
    """
    Parses a node string and returns a two-tuple of integers.
    
    A node string should be a letter character followed by one or two digits. So
    A1 and and B10 are valid node strings.
    """
    if re.match("^[A-Za-z]{1}[0-9]{1,2}$", node):
        return ord(node[0].upper())-65, int(node[1:])-1
    raise ParseError("Invalid node string.")

class TwixtServer(SocketServer.ThreadingTCPServer):
    """ The Twixt Server.
    
    Not really any different from the ThreadingTCPServer but has some attributes
    to ease the pain of setting up games of Twixt.
    
    Attributes:
        `users`
            A dictionary of the current users on this server.
        `pending_games`
            A list of user names who are waiting for someone to join their game.
        `games`
            A dictionary of currently running games.
    """
    # these class attributes let us kill the server without delay.
    daemon_threads = True
    allow_reuse_address = True
    def __init__(self, server_address, handler):
        SocketServer.ThreadingTCPServer.__init__(self, server_address, handler)
        self.users = {}
        self.pending_games = []
        self.games = {}
    
    
def require_game(meth):
    """
    Adding this decorator to a method will require the player to be involved in
    a game before the method can be called.
    """
    def wrapper(self, *args, **kwds):
        if not hasattr(self, "game"):
            return "ERR: Must participate in a game first."
        return meth(self, *args, **kwds)

def require_current(meth):
    """
    Adding this decorator to a method will require the player to be the current
    player before calling the method.
    """
    def wrapper(self, *args, **kwds):
        if not self.nick == self.game.current:
            return "ERR: Not your turn."
        return meth(self, *args, **kwds)

def message_waiting(meth):
    """
    This decorator keeps the waiting user informed of the current players 
    every (valid) move.
    """
    def wrapper(self, *args, **kwds):
        msg = meth(self, *args, **kwds)
        if not msg.startswith("ERR"): # don't bother the waiting user with ERR
            self.server.users[self.game.waiting].write(msg)
        return msg

def public(func):
    # decorator to expose a method of our Handler to the users.
    func.public = True
    return func

class TwixtHandler(SocketServer.StreamRequestHandler):
    
    def handle(self):
        # this method is called when someone connects to the TwixtServer.
        self._quit = False
        while not self._quit: # here is our main loop.
            cmd = self.rfile.readline() # get some input from user.
            try: # try to process it
                msg = self.proccess(cmd)
            except Exception, e:
                print e # this goes to the stdout of the server, not the 
                #         user.
                msg = "Internal error."
            if msg:
                self.wfile.write(msg) # this goes to the user.
                if not msg.endswith("\n"): # always end messages with \n
                    self.wfile.write("\n")
        del self.server.users[self.nick]
        self.server.pending_games.remove(self.nick)
    
    def proccess(self, cmd):
        if not cmd: # shortcut for the empty string
            return
        tokens = cmd.split() # split the commands into tokens
        c = tokens.pop(0) # the first token is the method we will call
        m = None
        if hasattr(self, c): # do we have this command?
            m = getattr(self, c)
        if not m or not hasattr(m, "public"): # is it public?
            return "ERR: No such command."
        try: # try to run the command we the remaining tokens as arguments
            msg = m(*tokens)
        except Exception, e:
            print e
            return "ERR: Some kind of problem."
        return msg
    
    @public
    def ident(self, nick): # this commamnd sets the users nick
        """ Set your `nick`. """
        if nick in self.server.users:
            return "ERR: Nick %s exists" % nick
        self.server.users[nick] = self.wfile
        self.nick = nick
        return
    
    @public
    def create(self):
        """ Create a new game. Blocks until other player joins. """
        # this command creates a game, and blocks while waiting for someone
        # to join.  Should probably make it non-blocking... but not sure
        # about the best way to do it. maybe add a new command `start` which
        # does all of the game setup once another player joins the game.
        self.server.pending_games.append(self.nick)
        # block here while waiting for player 2.
        while not self.nick in self.server.games:
            time.sleep(1)
        self.game = self.server.games[self.nick]
        # we attach some state information to the `Twixt` instance, 
        # but this is merely a convenience.  `Twixt` has no knowledge
        # of these attributes.
        self.game.current = self.game.player2
        self.game.waiting = self.game.player1
        return "Created game against %s." % self.game.player2
    
    @public
    def games(self):
        """ List all pending games. """
        # returns a list of games one could join.
        return ", ".join(self.server.pending_games)
    
    @public
    def join(self, nick):
        """ Join a game against `nick`. """
        # joins a game.
        if nick == self.nick:
            return "ERR: Can't join own game."
        if not nick in self.server.pending_games:
            return "ERR: No such game."
        self.server.pending_games.remove(nick)
        self.server.games[nick] = twixt.Twixt(nick, self.nick)
        self.game = self.server.games[nick]
        return "Joined game against %s." % nick
    
    @public
    @require_game
    @require_current
    @message_waiting
    def claim(self, node):
        """ Claim `node`. """
        # check state.
        if self.game.claimed: # can only claim a node once per turn.
            return "ERR: Already claimed a node this turn."
        # try to parse node.
        try:
            node_ = parse(node)
        except ParseError,e:
            return "ERR: Invalid node string."
        # try to claim `node`.
        try:
            self.game.claim_node(node_, self.nick)
            self.game.claimed = True
        except twixt.NodeError, e:
            return "ERR: %s" % str(e)
        return "claimed %s." % node
    
    # a note on connect disconnect:
    # Turn phase shouldn't really matter with regard to connect/disconnect.
    # there is no competitive advantage to being able to mix
    # connects/disconnects freely (none that I can see, anyway).
    
    @public
    @require_game
    @require_current
    @message_waiting
    def connect(self, node0, node1):
        """ Connect node0 to node1. """
        # parse the nodes.
        try:
            node0_, node1_ = parse(node0), parse(node1)
        except ParseError,e:
            return "ERR: Invalid node string."
        # try to connect node0 to node1.
        try:
            self.game.connect(node0_, node1_, self.nick)
        except twixt.NodeError, e:
            # show the user why these nodes can't connect.
            return "ERR: %s" % str(e)        
        return "connected %s-%s." % (node0, node1)
    
    @public
    @require_game
    @require_current
    @message_waiting
    def disconnect(self, node0, node1):
        """ Disconnect node0 from node1. """
        # try to disconnect node0 from node1.
        try:
            node0_, node1_ = parse(node0), parse(node1)
        except ParseError,e:
            return "ERR: Invalid node string."
        try:
            self.game.disconnect(node0_, node1_, self.nick)
        except twixt.NodeError, e:
            # show the user why these nodes can't disconnect.
            return "ERR: %s" % str(e)
        return "disconnected %s-%s." % (node0, node1)
    
    @public
    @require_game
    @require_current
    @message_waiting
    def end(self):
        """ End the turn. """
        # this method should also do the win-checking.
        game = self.game # make an alias to self.game to keep our lines short :)    
        game.current, game.waiting = game.waiting, game.current
        game.claimed = False
        if game.has_won(self.nick):
            return "%s has won!" % self.nick
        return "ended turn."
    
    @public
    def quit(self):
        """ Quits the server. """
        # quit the server.  logs out.
        self._quit = True
        return "Quitting server."
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: %s [hostname] [port number]' % sys.argv[0]
        sys.exit(1)
    
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    
    server = TwixtServer((hostname, port), TwixtHandler)
    server.serve_forever()