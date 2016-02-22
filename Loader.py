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

def loadDictionary( *filepaths, weightTransformationFct=(lambda x: x) ):
    dictionary = {}
    with fileinput.input( filepaths, openhook=fileinput.hook_encoded("UTF-8") ) as lines:
        for line in lines:
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
