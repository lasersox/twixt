from pyparsing import *
from twixt import Bridge, Peg

class Ord(TokenConverter):
    # Converts alpha letter into a num.
    def postParse(self, instring, loc, toklist):
        return map( lambda x: ord(x.upper())-64, toklist)
        
class Int(TokenConverter):
    # converts a alpha num into a num.
    def postParse(self, instring, loc, toklist):
        return map( lambda x: int(x), toklist )
        
class PegConverter(TokenConverter):
    # Converts a peg tuple into a Peg object.
    def postParse(self, instring, loc, toklist):
        return Peg(tuple(toklist))

class PegChainConverter(TokenConverter):
    # Converter to change a peg chain
    # into a list of Bridge objects.
    def postParse(self, instring, loc, toklist):
        bridges = []
        lastPeg = None
        for peg in toklist:
            if lastPeg != None:
                bridges.append(Bridge([lastPeg,peg]))
            lastPeg = peg
        return bridges

y = Ord(Word(alphas, max=1))
x = Int(Word(nums, max=2))
peg = PegConverter(y + x)
chain = PegChainConverter(peg + OneOrMore(Literal('/').suppress() + peg))
move = peg + Literal("-").suppress() + chain + Literal("+").suppress() + chain

def parse_peg(s):
    return peg.parseString(s)[0]

def parse_bridge(s):
   return chain.parseString(s)[0]

def parse_move(s):
    return move.parseString(s)