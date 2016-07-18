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

import argparse

import Selector
    
if __name__ != '__main__':
    raise Exception("This program is intented to be called interactively")
    


#Argument argparser name in terms of the argument tree path:
argparsedNameToPathMap = {
    'number' : ['number'],
    'seed' : ['seed'],
    'verbose' : ['verbose'],
    'gui' : ['gui','enabled'],
    'uniform' : ['lexicon','uniform'],
    'ignore_case' : ['lexicon','ignore-case'],
    'min_length' : ['filters','min-length'],
    'max_length' : ['filters','max-length'],
    'original' : ['filters','original'],
    'generator' : ['generator','default'],
    'files' : ['lexicon','files'],
    #markov
    'markov_ngram_size' : ['generator','markov','ngram-size'],
    #smooth-markov
    'smooth_markov_ngram_size' : ['generator','smooth-markov','ngram-size'],
}

#Convert a argparser name into a tree arborescence.
def argparsedToArgument( argsNamespace ):
    newArguments = Selector.Arguments()
    for key, value in vars( argsNamespace ).items():
        if value == None:
            continue
        newArguments.set( value, *argparsedNameToPathMap[key] )
    return newArguments

#Load config file into a tree arborescence
argparser = argparse.ArgumentParser(
        usage='%(prog)s [options] [LEXICON...]',
        description='Generate a random name from a flavor of existing names.'
        )

#general options
argparser.add_argument( '-n', '--number', action='store', type=int,
        help="number of names to generate" )
argparser.add_argument( '-S', '--seed', action='store', type=int,
        help="seed for the random generator.  If this option is not provided, the current system time is used as a seed." )
argparser.add_argument( '-G', '--gui', action='store_true', default=None,
        help="Load the program with the GUI." )
argparser.add_argument( '-B', '--batch', action='store_false', dest='gui' )
argparser.add_argument( '-v', '--verbose', action='store_true', default=None,
        help="print additional information like the perplexity." )
argparser.add_argument( '-q', '--quiet', action='store_false', dest='verbose' )
argparser.add_argument( '-u', '--uniform', action='store_true', default=None,
        help="ignore possible word weight and set them all to 1" )
argparser.add_argument( '--weighted', action='store_false', dest='uniform' )
argparser.add_argument( '-i', '--ignore-case', action='store_true', default=None,
        help="ignore case of lexicon files (generate all lowercase words)" )
argparser.add_argument( '--acknowledge-case', action='store_false', dest='ignore_case' )
argparser.add_argument( '-l', '--min-length', action='store', type=int,
        help="minimun length of a generated name" )
argparser.add_argument( '-L', '--max-length', action='store', type=int,
        help="maximum length of a generated name" )
argparser.add_argument( '-o', '--original', action='store_true', default=None,
        help="discard words already existing in the lexicon" )
argparser.add_argument( '-a', '--any', action='store_false', dest='original',
        help="allow to generate words already existing in the lexicon" )
argparser.add_argument( '-g', '--generator', metavar = 'ALGO', action='store',
        choices=['smooth-markov','markov'],
        help="""algorithm used to generate the names.
        Possible choices include 'markov', 'smooth-markov'.""" )
#markov options
argparser.add_argument( '--markov-ngram-size', metavar='SIZE', action='store', type=int,
        help="In the 'markov' algorihm, set how many previous characters are looked to choose the next one" )
#smooth markov options
argparser.add_argument( '--smooth-markov-ngram-size', metavar='SIZE', action='store', type=int,
        help="In the 'smooth-markov' algorihm, set how many previous characters are looked to choose the next one" )
#non-options arguments (lexicon files)
argparser.add_argument( 'files', metavar='FILE', action='store', nargs='*', default=argparse.SUPPRESS,
        help='dictonary files to learn names from' )

#Merge configuration files' arguments and cli-given arguments
arguments = Selector.loadDefaultArguments()
cli_arguments = argparsedToArgument( argparser.parse_args() )
arguments.update( cli_arguments )

#Custom tweaking of the arguments based on some CLI values
if cli_arguments.contains("number"):
    arguments.set( True, 'gui', '*autogenerate_at_start' )

#Set seed if required
seedValue = arguments.get('seed',default='auto')
if type(seedValue) == int:
    import random
    random.seed(int(seedValue))

#Choose to use GUI or Batch
if arguments.get('gui','enabled',default=False):
    import GUI
    GUI.process( arguments )
else:
    import Batch
    Batch.process( arguments )


