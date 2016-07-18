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

INITIAL_CHAR = '\x02'
TERMINAL_CHAR = '\x03'

class PrefixCounter(object):
    def __init__( self,
            dictionary,
            minlength = 0,
            maxlength = 2,
            generateDelimiterSymbols = True,
            ):
        assert type(minlength) == int
        assert type(maxlength) == int
        assert type(generateDelimiterSymbols) == bool

        self.minlength_ = minlength
        self.maxlength_ = maxlength
        self.characters_ = set()
        
        self.prefixCounters_ = buildPrefixCounters(
                dictionary=dictionary,
                minlength=minlength,
                maxlength=maxlength,
                generateDelimiterSymbols=generateDelimiterSymbols,
                encounteredCharacters= self.characters_
                )
        self.characters_ = list( sorted( self.characters_ ) )
    
    def characters( self ):
        yield from self.characters_
    
    def perCharacterPrefixOccurences( self, length, prefix ):
        assert length == None or type(length) == int
        assert type(prefix) == str
        
        if prefix not in self.prefixCounters_[length]:
            return None
        yield from sorted( self.prefixCounters_[ length ][ prefix ].items() )

    def countPrefixOccurences( self, length, prefix ):
        assert length == None or type(length) == int
        assert type(prefix) == str
        
        if prefix not in self.prefixCounters_[length]:
            return 0
        s = sum( self.prefixCounters_[length][prefix].values() )
        return s
    
    def rangeTuple( self ):
        return ( self.minlength_, self.maxlength_ )


    def printCountTable( self, length ):
        print( "     ", "|".join( map(normalizeStr,self.characters()) ) )
        print( "-----", "+".join( map(lambda e:"----",self.characters()) ) )
        for p in sorted(self.prefixCounters_[length]):
            print( normalizeStr(p), end='||' )
            for c in self.characters():
                if c in self.prefixCounters_[length][p]:
                    v = self.prefixCounters_[length][p][c]
                    print( "% 4d"%(v,), end='|' )
                else:
                    print(" "*4, end='|')
            print()

def buildPrefixCounters(
        dictionary,
        minlength = 0,
        maxlength = 2,
        generateDelimiterSymbols = True,
        encounteredCharacters = None ):

    prefixCounters = { i : {} for i in range(minlength,maxlength+1) }
    for word, weight in dictionary.items():
        if generateDelimiterSymbols:
            word = (INITIAL_CHAR,) + word + (TERMINAL_CHAR,)
        ngrams = { j : '' for j in range(minlength+1,maxlength+2) }
        for c in word:
            if encounteredCharacters != None:
                encounteredCharacters.add( c )
            for j in range(minlength+1,maxlength+2):
                ngrams[j] += c
                if len(ngrams[j]) > j:
                    ngrams[j] = ngrams[j][1:]

                prefix = ngrams[j][:-1]
                character = ngrams[j][-1]
                if character == INITIAL_CHAR:
                    continue
                i = j-1
                if prefix not in prefixCounters[i]:
                    prefixCounters[i][ prefix ] = {}
                if character not in prefixCounters[i][ prefix ]:
                    prefixCounters[i][ prefix ][ character ] = 0
                prefixCounters[i][ prefix ][ character ] += weight
    return prefixCounters


class Scorer(object):
    def __init__( self ):
        self.scores_ = {}

    ## c = the character itself
    ## l = effective length of prefix (may be higher than actual length to account for start_of_word prefixes)
    ## n = number of occurences of the prefix
    ## k = number of occurenecs of the character after the prefix
    def learn( self, l, c, n, k ):
        score = (k/n) * 2**l
        if c in self.scores_:
            self.scores_[c] += score
        else:
            self.scores_[c] = score
        
    def reset( self ):
        self.scores_ = {}

    def scores( self ):
        yield from sorted( self.scores_.items() )


class Generator(object):
    def __init__(
            self,
            dictionary,
            minNGramLength = 0,
            maxNGramLength = 2,
            generateDelimiterSymbols = True,
            minNameLength=0,
            maxNameLength=256 ):

        self.prefixCounter_ = PrefixCounter( dictionary,
                minlength = minNGramLength,
                maxlength = maxNGramLength,
                generateDelimiterSymbols = generateDelimiterSymbols )
        self.scorer_ = Scorer()
        self.minNameLength_ = minNameLength
        self.maxNameLength_ = maxNameLength
        
    def generateName( self ):
        name = INITIAL_CHAR
        probabilityOfName = 1.0
        while len(name) < self.maxNameLength_ + 1:
            ngramLengths = self.prefixCounter_.rangeTuple()
            minNgramLength = ngramLengths[0]
            maxNGramLength = min( ngramLengths[1], len(name) )
            for length in range(minNgramLength,maxNGramLength+1):
                prefix = name[-length:] if length > 0 else ''
                totalOccurences = self.prefixCounter_.countPrefixOccurences( length, prefix )
                perCharOccurences = list( self.prefixCounter_.perCharacterPrefixOccurences( length, prefix ) )

                for char, charOccurences in perCharOccurences:
                    self.scorer_.learn( length, char, totalOccurences, charOccurences )

            characters_only, strengths_only = zip(* self.scorer_.scores() )
            i = discretepick( strengths_only )
            character = characters_only[i]
            if character == TERMINAL_CHAR:
                if len(name) < self.minNameLength_:
                    continue
                else:
                    break
            name += character
            probabilityOfName *= strengths_only[i] / sum(strengths_only)
            
            self.scorer_.reset()
        
        name=name[1:]
        namePerplexity = (probabilityOfName**(-1/len(name))) if len(name)>0 else 0
        
        return ( namePerplexity, name )
        


def normalizeStr( c, l=4 ):
    c = repr(c)[1:-1][:l]
    c = " "*(l-len(c)) + c
    return c


