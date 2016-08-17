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

#TODO management of symbolic links
def findFilesFromDir( path ):
    files = []
    for name in os.listdir( path ):
        subpath = os.path.join(path,name)
        if os.path.isdir( subpath ):
            files += findFilesFromDir( subpath )
        else:
            files.append( subpath )
    return files

def findFilesFromPattern( pattern ):
    files = []
    for path in iglob( pattern ):
        if os.path.isdir( path ):
            files += findFilesFromDir( path )
        else:
            files.append( path )
    return files
        
def findFilesFromPatterns( patterns ):
    files = []
    for pattern in patterns:
        files += findFilesFromPattern( pattern )
    return files

def findFilesFromPaths( paths ):
    files = []
    for path in paths:
        if os.path.isdir( path ):
            files += findFilesFromDir( path )
        else:
            files.append( path )
    return files
    
            
def loadLexiconFile( *lexiconFilepaths ):
    if len(lexiconFilepaths) == 0:
        return {}

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
    return loadLexiconFile( *findFilesFromPaths( [filepath] ) )


def loadLexicons( filepaths ):
    return loadLexiconFile( *findFilesFromPaths( filepaths ) )


def loadLexiconsFromPattern( pattern ):
    return loadLexiconFile( *findFilesFromPattern( pattern ) )


def loadLexiconsFromPatterns( patterns ):
    return loadLexiconFile( *findFilesFromPatterns( patterns ) )


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

class InvalidGeneratedWord(Exception):
    def __init__( self, message, word, weight ):
        self.message = message if message != None else "Partially generated word is invalid."
        self.word = word
        self.weight = weight
    def __str__( self ):
        return self.message


