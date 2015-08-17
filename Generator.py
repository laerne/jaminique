#/usr/bin/env python3
from utilities import discretepick

class AdditiveExponentialScorer():
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


class SimpleLagrangeGenerator:
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

if __name__ == '__main__':
    import argparse
    import PrefixCounter
    argparser = argparse.ArgumentParser(
            usage='%(prog)s [options] dictionary [dictionary...]',
            description='Generate a random name from a flavor of existing names.'
            )

    argparser.add_argument( '-n', '--number', action='store', type=int, default=1,
            help='number of names to generate' )
    argparser.add_argument( '-u', '--uniform', action='store_true', default=False,
            help='ignore possible word weight and set them all to 1' )
    argparser.add_argument( '-s', '--ngram-size', action='store', type=int, default=2,
            help='how many previous characters are looked to choose the next one (default 2)' )
    argparser.add_argument( '-l', '--min-length', action='store', type=int, default=3,
            help='minimun length of a generated name (default 3)' )
    argparser.add_argument( '-L', '--max-length', action='store', type=int, default=20,
            help='maximum length of a generated name (default 20)' )
    argparser.add_argument( '-o', '--original', action='store_true', default=False,
            help='discard words already existing in the dictionary' )
    argparser.add_argument( '-p', '--min-perpexity', action='store', type=float, default=0.0,
            help='tolerance threshold to discard words that matches too closely the examples (default 0.0)' )
    argparser.add_argument( '-P', '--max-perpexity', action='store', type=float, default=10,
            help='tolerance threshold to discard ugly words (default 10.0)' )
    argparser.add_argument( 'dictionary', metavar='FILE', action='store', nargs='*',
            default=['namelists/viking_male.txt','namelists/viking_female.txt','namelists/viking_unknownGender.txt'],
            help='Dictonary files to learn names from' )

    args = argparser.parse_args()

    dictionary = PrefixCounter.loadDictionary( *args.dictionary )
    prefixCounter = PrefixCounter.PrefixCounter( dictionary, minlength=0, maxlength=args.ngram_size, generateDelimiterSymbols=True )
    generator = SimpleLagrangeGenerator( prefixCounter, minlength = args.min_length, maxlength = args.max_length )
    
    n = 0
    while n < args.number:
        namePerplexity, name = generator.generateName()
        if args.original and (name in dictionary) :
            pass
            #print("%.6f!: %s" % (namePerplexity, name) )
        elif namePerplexity > args.max_perpexity:
            pass
            #print("%.6f>: %s" % (namePerplexity, name) )
        elif namePerplexity < args.min_perpexity:
            pass
            #print("%.6f<: %s" % (namePerplexity, name) )
        else:
            print("%.6f :: %s" % (namePerplexity, name) )
            n +=1

