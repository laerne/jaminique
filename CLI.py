import PrefixCounter
import Loader
import Generator
import argparse
    
if __name__ != '__main__':
    raise Exception("This program is intented to be called interactively")

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

dictionary = Loader.loadDictionary( *args.dictionary )
prefixCounter = PrefixCounter.PrefixCounter( dictionary, minlength=0, maxlength=args.ngram_size, generateDelimiterSymbols=True )
generator = Generator.SimpleLagrangeGenerator( prefixCounter, minlength = args.min_length, maxlength = args.max_length )

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


