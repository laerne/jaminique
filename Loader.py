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
import os
from glob import iglob


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
            
def loadLexiconDir( *filepaths ):
    actualLexiconPaths = selectFilesFromDirs( *filepaths )
    return loadLexicon( *actualLexiconPaths )
            

def loadLexiconFile( *lexiconFilepaths ):
    lexicon = {}
    with fileinput.input( lexiconFilepaths, openhook=fileinput.hook_encoded("UTF-8") ) as lines:
        for line in lines:
            item = line.split('#',maxsplit=1)[0].strip()
            tokens = item.rsplit( ':', maxsplit=1 )
            word = tokens[0]
            if word == '':
                continue
                
            try:
                weight = float(tokens[1]) if len( tokens ) >= 2 else 1.0
            except ValueError as e:
                warn( "Incorrect weight value %s.  Defaulting to 1." % repr(tokens[1]) )
                weight = 1.0
            if word in lexicon:
                lexicon[word] += weight
            else:
                lexicon[word] = weight
    return lexicon

def loadLexicon( filepath ):
    if os.path.isdir( filepath ):
        childrenpaths = map(
                lambda name: os.path.join( filepath, name ),
                os.listdir( filepath ) )
        return loadLexicons( childrenpaths )
    else:
        return loadLexiconFile( filepath )


def loadLexicons( filepaths ):
    return mergeLexicons( map( loadLexicon, filepaths ) )


def loadLexiconsFromPattern( pattern ):
    lexicons = map( loadLexicon, iglob( pattern ) )
    return mergeLexicons( lexicons )


def loadLexiconsFromPatterns( patterns ):
    lexicons = []
    for pattern in patterns:
        lexicons += map( loadLexicon, iglob( pattern ) )
    return mergeLexicons( lexicons )


def mergeLexicons( dictionaries ):
    merged = {}
    for lexicon in dictionaries:
        for key, value in lexicon.items():
            if key in merged:
                merged[key] += value
            else:
                merged[key] = value
    return merged

def mergeLexicon( *dictionaries ):
    return mergeLexicons( dictionaries )
