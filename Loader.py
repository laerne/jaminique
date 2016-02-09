#/usr/bin/env python3
import fileinput
from utilities import warn, fail

def loadDictionary( *filepaths, weightTransformationFct=(lambda x: x) ):
    dictionary = {}
    for line in fileinput.input( filepaths ):
        item = line.split('#')[0].strip()
        tokens = item.split(':')
        word = tokens[0]
        if word == '':
            continue
        try:
            weight = float(tokens[1]) if len( tokens ) > 2 else 1
        except ValueError as e:
            from utilities import warn
            warn( "Incorrect weight value.  Defaulting to 1." )
            weight = 1
        weight = weightTransformationFct( weight )
        if word in dictionary:
            dictionary[word] += weight
        else:
            dictionary[word] = weight
    return dictionary


def mergeDictionaries( *dictionaries ):
    merged = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if key in merged:
                merged[key] += value
            else:
                merged[key] = value
    return merged
    
def mergeDictionary( editedDictionary, appendedDictionary ):
    for key, value in appendedDictionary.items():
        if key in editedDictionary:
            editedDictionary[key] += value
        else:
            editedDictionary[key] = value
    return editedDictionary
