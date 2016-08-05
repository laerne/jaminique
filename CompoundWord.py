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

from utilities import DiscretePicker

class Generator(object):
    def __init__(
            self,
            lexicon,
            length_rv,
            ):
        self.lexicon_ = sorted( lexicon.items() )
        self.length_random_variable_ = length_rv
        self.word_index_picker_ = DiscretePicker( [ w for (k,w) in self.lexicon_ ] )

    def generateName( self ):
        length = self.length_random_variable_.pick()
        portmanteau = ""
        weight = 0.0
        
        for i in range( length ):
            k = self.word_index_picker_.pick()
            
            ith_word = self.lexicon_[ k ][0]
            ith_weight = self.lexicon_[ k ][1]
            
            portmanteau += "".join( ith_word )
            weight += ith_weight
            
        return weight, portmanteau
            
