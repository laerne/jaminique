#/usr/bin/env python3

class PrefixCounter(object):
    def __init__( self,
            dictionary,
            minlength = 0,
            maxlength = 2,
            generateDelimiterSymbols = False,
            generateShorterPrefixes = False
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
    
    def characters( self ):
        yield from self.characters_
    
    def perCharacterPrefixOccurences( self, length, prefix ):
        assert length == None or type(length) == int
        assert type(prefix) == str
        
        if prefix not in self.prefixCounters_[length]:
            return {}
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
        characters = sorted( self.characters_ )
        print( "     ", "|".join( map(normalizeStr,characters) ) )
        print( "-----", "+".join( map(lambda e:"----",characters) ) )
        for p in sorted(self.prefixCounters_[length]):
            print( normalizeStr(p), end='||' )
            for c in characters:
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
            word = '^' + word + '$'
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
                if character == '^':
                    continue
                i = j-1
                if prefix not in prefixCounters[i]:
                    prefixCounters[i][ prefix ] = {}
                if character not in prefixCounters[i][ prefix ]:
                    prefixCounters[i][ prefix ][ character ] = 0
                prefixCounters[i][ prefix ][ character ] += weight
    return prefixCounters



def normalizeStr( c, l=4 ):
    c = repr(c)[1:-1][:l]
    c = " "*(l-len(c)) + c
    return c

### TEST ###
if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(
            usage='%(prog)s [options] dictionary [dictionary...]',
            description='Unit test: build digrams from given dictionary and give a table count of them.',
            )

    argparser.add_argument( 'dictionary', action='store', nargs='*',
            default=['namelists/viking_male.txt','namelists/viking_female.txt','namelists/viking_unknownGender.txt'],
            help='Dictionary of name to learn from.' )

    args = argparser.parse_args()
    
    dictionary = loadDictionary( *args.dictionary )
    prefixCounter = PrefixCounter( dictionary, minlength = 0, maxlength = 2, generateDelimiterSymbols = True )
    prefixCounter.printCountTable(2)
    for p in sorted( prefixCounter.prefixCounters_[1] ):
        print( "total(%s): %d" % ( repr(p), prefixCounter.countPrefixOccurences(1,p) ) )

