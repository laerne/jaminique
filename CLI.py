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

from ArgumentTree import ArgumentTree
import Selector

import argparse
    
if __name__ != '__main__':
    raise Exception("This program is intented to be called interactively")
    


#Argument argparser name in terms of the argument tree path:
argparsedNameToPathMap = {
    'number' : ['number'],
    'seed' : ['seed'],
    'verbose' : ['verbose'],
    'gui' : ['gui','enabled'],
    'tokenizer' : ['tokenizer','default'],
    'generator' : ['generator','default'],
    'filters' : ['filters','default'],
    'files' : ['lexicon','files'],
}

#Convert a argparser name into a tree arborescence.
def argparsedToArgument( argsNamespace ):
    newArguments = ArgumentTree()
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
        help="load the program with the GUI." )
argparser.add_argument( '-B', '--batch', action='store_false', dest='gui',
        help="run the program non-interactively." )
argparser.add_argument( '-v', '--verbose', action='store_true', default=None,
        help="print additional information like the perplexity." )
argparser.add_argument( '-q', '--quiet', action='store_false', dest='verbose',
        help="do not print additional information like the perplexity." )
argparser.add_argument( '-t', '--tokenizer', metavar = 'PRESET', action='store',
        help="""algorithm or preset used to split characters/phonems from the names.""")
argparser.add_argument( '-g', '--generator', metavar = 'PRESET', action='store',
        help="""algorithm or preset used to generate the names.""" )
argparser.add_argument( '-f', '--filters', metavar = 'PRESET', action='store',
        help="""Presets of filters to apply on generated names.""" )

#non-options arguments (lexicon files)
argparser.add_argument( 'files', metavar='FILE', action='store', nargs='*', default=argparse.SUPPRESS,
        help='dictonary files to learn names from' )

#Merge configuration files' arguments and cli-given arguments
arguments = Selector.loadDefaultArgumentTree()
cli_arguments = argparsedToArgument( argparser.parse_args() )
arguments.update( cli_arguments )

#Custom tweaking of the arguments based on some CLI values
if cli_arguments.contains("number"):
    arguments.set( True, 'gui', '<autogenerate_at_start>' )

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


