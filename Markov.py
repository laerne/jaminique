# This file is part of Jaminique.
# Copyright (C) 2016 by Nicolas BRACK <nicolas.brack@mail.be>
# 
# Jaminique is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Jaminique is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Jaminique.  If not, see <http://www.gnu.org/licenses/>.

from utilities import discretepick

class TransitionTable(object):
    def __init__( self,
            dictionary,
            length = 2,
            ):
        assert type(length) == int

        self.length_ = length
        self.characters_ = set()
        
        self.table_ = buildTransitionTable(
                dictionary=dictionary,
                length=length,
                encounteredCharacters= self.characters_
                )
        self.characters_ = sorted( self.characters_ )
    
    def characters( self ):
        yield from self.characters_
    
    def transitionsForPrefix( self, prefix ):
        assert type(prefix) == str
        
        if prefix not in self.table_:
            return None
        yield from sorted( self.table_[ prefix ].items() )

    def prefixScore( self, prefix ):
        assert type(prefix) == str
        
        if prefix not in self.table_:
            return 0
        s = sum( self.table_[prefix].values() )
        return s
    
    def length( self ):
        return self.length_
        
    def printCountTable( self ):
        print( "     ", "|".join( map(normalizeStr,self.characters()) ) )
        print( "-----", "+".join( map(lambda e:"----",self.characters()) ) )
        for p in sorted(self.table_):
            print( normalizeStr(p), end='||' )
            for c in self.characters():
                if c in self.table_[p]:
                    v = self.table_[p][c]
                    print( "% 4d"%(v,), end='|' )
                else:
                    print(" "*4, end='|')
            print()

def normalizeStr( c, l=4 ):
    c = repr(c)[1:-1][:l]
    c = " "*(l-len(c)) + c
    return c


def buildTransitionTable(
        dictionary,
        length = 2,
        encounteredCharacters = None ):

    prefixCounters = {}
    for word, weight in dictionary.items():
        word = '^' + word + '$'
        ngram = ''
        for c in word:
            if encounteredCharacters != None:
                encounteredCharacters.add( c )
                ngram += c
                if len(ngram) > length:
                    ngram = ngram[1:]

                prefix = ngram[:-1]
                character = ngram[-1]
                if character == '^':
                    continue
                if prefix not in prefixCounters:
                    prefixCounters[ prefix ] = {}
                if character not in prefixCounters[ prefix ]:
                    prefixCounters[ prefix ][ character ] = 0
                prefixCounters[ prefix ][ character ] += weight
    return prefixCounters

class Generator(object):
    def __init__(
            self,
            dictionary,
            nGramLength = 2,
            minNameLength=0,
            maxNameLength=256 ):

        self.nGramLength_ = nGramLength
        self.transitionTable_ = TransitionTable( dictionary, length = nGramLength+1 )
        self.minNameLength_ = minNameLength
        self.maxNameLength_ = maxNameLength
        
    def generateName( self ):
        name = '^'
        probabilityOfName = 1.0
        while len(name) < self.maxNameLength_ + 1:
            prefix = name[-self.nGramLength_:] if self.nGramLength_ > 0 else ''
            #prefixScore = self.transitionTable_.prefixScore( prefix )
            
            transitions = list( self.transitionTable_.transitionsForPrefix( prefix ) )
            if not transitions:
                self.transitionTable_.printCountTable()
                break
            transitionCharacters, transitionScores = zip( *transitions )
            
            i = discretepick( transitionScores )
            character = transitionCharacters[i]
            
            if character == '$':
                if len(name) < self.minNameLength_:
                    continue
                else:
                    break

            name += character
            probabilityOfName *= transitionScores[i] / sum(transitionScores)
            
        
        name=name[1:]
        namePerplexity = (probabilityOfName**(-1/len(name))) if len(name)>0 else 0
        
        return (namePerplexity, name)
