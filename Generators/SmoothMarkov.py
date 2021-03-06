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

from utilities import perplx, discretepick, warn
from .Exceptions import InvalidGeneratedWord

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


def exponential_length_score_fct( l, n, k ):
    return (k/n) * 2**l
    
def quadratic_length_score_fct( l, n, k ):
    return (k/n) * l**2

def linear_score_fct( l, n, k ):
    return (k/n) * l

def str_to_score_fct( fct_name ):
    fct_name = fct_name.lower()
    if fct_name == "linear":
        return linear_score_fct
    elif fct_name == "quadratic":
        return quadratic_length_score_fct
    elif fct_name == "exponential":
        return exponential_length_score_fct

class FunctionalScorer(object):
    def __init__( self, score_fct = exponential_length_score_fct ):
        self.scores_ = {}
        self.score_fct_ = score_fct

    ## c = the character itself
    ## l = effective length of prefix (may be higher than actual length to account for start_of_word prefixes)
    ## n = number of occurences of the prefix
    ## k = number of occurenecs of the character after the prefix
    def learn( self, prefix_length, character, n_prefixes, n_prefix_characters ):
        score = self.score_fct_( prefix_length, n_prefixes, n_prefix_characters )
        if character in self.scores_:
            self.scores_[character] += score
        else:
            self.scores_[character] = score
        
    def reset( self ):
        self.scores_ = {}

    def scores( self ):
        yield from sorted( self.scores_.items() )


class SmoothMarkovGenerator(object):
    def __init__(
            self,
            dictionary,
            minNGramLength = 0,
            maxNGramLength = 2,
            generateDelimiterSymbols = True,
            minNameLength = 0,
            maxNameLength = 256 ):

        self.prefixCounter_ = PrefixCounter( dictionary,
                minlength = minNGramLength,
                maxlength = maxNGramLength,
                generateDelimiterSymbols = generateDelimiterSymbols )
        self.scorer_ = FunctionalScorer()
        self.minNameLength_ = minNameLength
        self.maxNameLength_ = maxNameLength
        
    def generateName( self ):
        name = INITIAL_CHAR
        probabilityOfName = 1.0
        while len(name) < self.maxNameLength_ + 1:
            minNgramLength, maxNGramLength = self.prefixCounter_.rangeTuple()
            #Do not try to have prefixes longer that what was already generated
            maxNGramLength = min( maxNGramLength, len(name) )

            #Compute weights to choose next character
            for length in range(minNgramLength,maxNGramLength+1):
                prefix = name[-length:] if length > 0 else ''
                totalOccurences = self.prefixCounter_.countPrefixOccurences( length, prefix )
                perCharOccurences = list( self.prefixCounter_.perCharacterPrefixOccurences( length, prefix ) )

                for char, charOccurences in perCharOccurences:
                    self.scorer_.learn( length, char, totalOccurences, charOccurences )


            transitionCharacters, transitionScores = map(   list,zip( *self.scorer_.scores() )   )
            
            #Discard the possibility to finish the name if not enough characters were generated.
            if len(name) < self.minNameLength_:
                if TERMINAL_CHAR in transitionCharacters:
                    i = transitionCharacters.index( TERMINAL_CHAR )
                    del transitionCharacters[i]
                    del transitionScores[i]

            #If there is no meaningful character to follow the prefix, raise an exception
            #( Should never happen if `minNGramLength == 0`, since then the empty prefix is used and any character
            #that appears in the lexicon can be picked with at least very unlikely prabilities.
            if len(transitionCharacters) <= 0:
                namePerplexity = perplx( probabilityOfName, len(name) )
                raise InvalidGeneratedWord( ("No character to transition from \"%s\""%prefix), name, namePerplexity )

            #Pick nexct character and build name
            i = discretepick( transitionScores )
            character = transitionCharacters[i]

            if character == TERMINAL_CHAR:
                break

            name += character
            probabilityOfName *= transitionScores[i] / sum(transitionScores)
            
            self.scorer_.reset()
        
        name=name[1:]
        namePerplexity = perplx( probabilityOfName, len(name) )

        return ( namePerplexity, name )
        


def normalizeStr( c, l=4 ):
    c = repr(c)[1:-1][:l]
    c = " "*(l-len(c)) + c
    return c


