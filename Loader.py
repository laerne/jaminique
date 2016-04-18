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

import fileinput
from utilities import warn, fail

import os.path
from glob import glob, iglob


def selectFilesFromDirs( *filepaths ):
    candidates = list( filepaths )
    dictionaries = []
    while len(candidates) > 0:
        candidate = candidates.pop(0)
        if os.path.isdir( candidate ):
            for subfile in subfiles(candidate):
                candidates.append( subfiles )
        elif os.path.splitext( candidate )[1] == '.txt':
            dictionaries.append( candidate )
        else:
            pass
            
def loadDictionaryDir( *filepaths,
        uniformWeights = False,
        forceLowerCase = False ):
    actualDictionaryPaths = selectFilesFromDirs( *filepaths )
    return loadDictionary( *actualDictionaryPaths )
            

def loadDictionary( *filepaths,
        uniformWeights = False,
        forceLowerCase = False ):
    dictionary = {}
    with fileinput.input( filepaths, openhook=fileinput.hook_encoded("UTF-8") ) as lines:
        for line in lines:
            item = line.split('#')[0].strip()
            tokens = item.split(':')
            word = tokens[0]
            if forceLowerCase:
                word = word.lower()
            if word == '':
                continue
                
            try:
                weight = float(tokens[1]) if not uniformWeights and len( tokens ) >= 2 else 1.0
            except ValueError as e:
                from utilities import warn
                warn( "Incorrect weight value.  Defaulting to 1." )
                weight = 1.0
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
