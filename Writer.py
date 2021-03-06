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

def writeLexicon( filepath, lexicon ):
    writeLexiconFromIterator( filepath, lexicon.items() )
            
def writeLexiconFromIterator( filepath, lexiconIterator ):
    with open( filepath, 'wt' ) as outputStream:
        for word, perplexity in lexiconIterator:
            outputStream.write( "%s:%f\n" % (word,perplexity) )
