#/usr/bin/env python3

import random

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

