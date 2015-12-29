#/usr/bin/env python3
from utilities import discretepick

class AdditiveExponentialScorer(object):
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


class SimpleLagrangeGenerator(object):
    def __init__( self, prefixCounter, scorer=AdditiveExponentialScorer, minlength=3, maxlength=24 ):
        self.prefixCounter_ = prefixCounter
        self.scorer_ = scorer()
        self.minNameLength_ = minlength
        self.maxNameLength_ = maxlength
        
    def generateName( self ):
        name = '^'
        probabilityOfName = 1.0
        while len(name) < self.maxNameLength_ + 1:
            ngramLengths = self.prefixCounter_.rangeTuple()
            minNgramLength = ngramLengths[0]
            maxNgramLength = min( ngramLengths[1], len(name) )
            for length in range(minNgramLength,maxNgramLength+1):
                prefix = name[-length:] if length > 0 else ''
                totalOccurences = self.prefixCounter_.countPrefixOccurences( length, prefix )
                perCharOccurences = list( self.prefixCounter_.perCharacterPrefixOccurences( length, prefix ) )

                for char, charOccurences in perCharOccurences:
                    self.scorer_.learn( length, char, totalOccurences, charOccurences )

            characters_only, strengths_only = zip(* self.scorer_.scores() )
            i = discretepick( strengths_only )
            character = characters_only[i]
            if character == '$':
                if len(name) < self.minNameLength_:
                    continue
                else:
                    break
            name += character
            probabilityOfName *= strengths_only[i] / sum(strengths_only)
            
            self.scorer_.reset()
        
        name=name[1:]
        namePerplexity = (probabilityOfName**(-1/len(name)))
        
        return (namePerplexity, name)
