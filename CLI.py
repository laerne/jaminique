#/usr/bin/env python3

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

import Loader
import SmoothMarkov
import Markov
import argparse
    
if __name__ != '__main__':
    raise Exception("This program is intented to be called interactively")

argparser = argparse.ArgumentParser(
        usage='%(prog)s [options] dictionary [dictionary...]',
        description='Generate a random name from a flavor of existing names.'
        )

#general options
argparser.add_argument( '-n', '--number', action='store', type=int, default=1,
        help="number of names to generate" )
argparser.add_argument( '-u', '--uniform', action='store_true', default=False,
        help="ignore possible word weight and set them all to 1" )
argparser.add_argument( '-i', '--ignore-case', action='store_true', default=False,
        help="ignore case of dictionary files (generate all lowercase words)" )
argparser.add_argument( '-l', '--min-length', action='store', type=int, default=3,
        help="minimun length of a generated name (default 3)" )
argparser.add_argument( '-L', '--max-length', action='store', type=int, default=20,
        help="maximum length of a generated name (default 20)" )
argparser.add_argument( '-p', '--min-perpexity', action='store', type=float, default=0.0,
        help="tolerance threshold to discard words that matches too closely the examples (default 0.0)" )
argparser.add_argument( '-P', '--max-perpexity', action='store', type=float, default=10,
        help="tolerance threshold to discard ugly words (default 10.0)" )
argparser.add_argument( '-o', '--original', action='store_true', default=False,
        help="discard words already existing in the dictionary" )
argparser.add_argument( '-S', '--seed', action='store', type=int,
        help="seed for the random generator.  If this option is not provided, the current system time is used as a seed." )
argparser.add_argument( '-v', '--verbose', action='store_true', default=False,
        help="print additional information like the perplexity." )
argparser.add_argument( '-a', '--algo', metavar = 'ALGO', action='store', default='smooth-markov',
        choices=['smooth-markov','markov'],
        help="""algorithm used to generate the names.
        Possible choices include 'markov', 'smooth-markov' (default "markov").""" )
        
#markov options
argparser.add_argument( '--markov-ngram-size', metavar='SIZE', action='store', type=int, default=3,
        help="In the 'markov' algorihm, set how many previous characters are looked to choose the next one (default 3)" )
        
#smooth markov options
argparser.add_argument( '--smooth-markov-ngram-size', metavar='SIZE', action='store', type=int, default=2,
        help="In the 'smooth-markov' algorihm, set how many previous characters are looked to choose the next one (default 2)" )
        
#non-options arguments (dictionary files)
argparser.add_argument( 'dictionary', metavar='FILE', action='store', nargs='*',
        default=['namelists/viking_male.txt','namelists/viking_female.txt','namelists/viking_unknownGender.txt'],
        help='dictonary files to learn names from' )

args = argparser.parse_args()

if args.seed:
    import random
    random.seed(args.seed)
dictionary = Loader.loadDictionary( *args.dictionary, forceLowerCase = args.ignore_case )

if args.algo == 'markov':
    generator = Markov.Generator( 
            dictionary,
            nGramLength = 3,
            generateDelimiterSymbols = True,
            minNameLength = args.min_length,
            maxNameLength = args.max_length )
elif args.algo == 'smooth-markov':
    generator = SmoothMarkov.Generator( 
            dictionary,
            minNGramLength = 0,
            maxNGramLength = args.smooth_markov_ngram_size,
            generateDelimiterSymbols = True,
            minNameLength = args.min_length,
            maxNameLength = args.max_length )
else:
    raise Exception("Invalid generator name given.")

n = 0
while n < args.number:
    namePerplexity, name = generator.generateName()
    if args.verbose and args.original and (name in dictionary) :
        print("%.6f!: %s" % (namePerplexity, name) )
    elif args.verbose and namePerplexity > args.max_perpexity:
        print("%.6f>: %s" % (namePerplexity, name) )
    elif args.verbose and namePerplexity < args.min_perpexity:
        print("%.6f<: %s" % (namePerplexity, name) )
    else:
        if args.verbose:
            print("%.6f :: %s" % (namePerplexity, name) )
        else:
            print("%s" % name )
        n +=1


