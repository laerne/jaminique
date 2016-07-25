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

import random
import sys

def printerror( label, *msgs, **kwargs ):
    if 'file' not in kwargs:
        kwargs['file'] = sys.stderr
    print( label, *msgs, **kwargs )

def warn( *msgs, **kwargs ):
    printerror( "Warning:", *msgs, **kwargs )
    
def fail( *msgs, **kwargs ):
    printerror( "Error:", *msgs, **kwargs )
    exception_msg = "Error: " + " ".join(map(str,msgs))
    raise Exception( exception_msg )

#verbosityLevel = 1
#def printVerbose( verbosity, *items ):
#    if( verbosity >= verbosityLevel ):
#        print( *items )

def dichotomicfind( random_access_collection, element ):
    i = 0
    j = len( random_access_collection )
    while i < j:
        k = (i+j) // 2
        if random_access_collection[k] > element:
            j = k
        elif random_access_collection[k] < element:
            i = k + 1
        else: #random_access_collection[k] == element
            return k
    assert i==j
    return i


def perplx( p, n ):
    return (p**(-1/n)) if n>0 else 0

class DiscretePicker:
    def __init__( self, probabilities ):
        self.cumulative_probabilities = []
        accumulator = 0.0
        
        self.indices = []
        i = -1
        for p in probabilities:
            i+=1
            if p == 0.0:
                continue
            accumulator += p
            self.cumulative_probabilities.append( accumulator )
            self.indices.append(i)

    def pick( self ):
        upper_bound = self.cumulative_probabilities[-1]
        random_float = random.uniform(0.0,upper_bound)
        return self.indices[ dichotomicfind( self.cumulative_probabilities, random_float ) ]

def discretepick( probabilities ):
    picker = DiscretePicker( probabilities )
    return picker.pick()


class InvalidGeneratedWord(Exception):
    def __init__( self, message, word, weight ):
        self.message = message if message != None else "Partially generated word is invalid."
        self.word = word
        self.weight = weight
    def __str__( self ):
        return self.message
