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


class AggregateFilter:
    def __init__( self, subfilters ):
        self.subfilters = subfilters

    def validate( self, name ):
        for f in self.subfilters:
            if not f.validate( name ):
                return False
        return True

    def add_subfilter( self, subfilter ):
        self.subfilters.append( subfilter )

    def del_subfilter( self, subfilter ):
        i = self.subfilters.index( subfilter )
        del self.subfilters[ i ]


class OriginalOnlyFilter:
    def __init__( self, namelist ):
        self.namelist = namelist
    
    def validate( self, name ):
        return ( "".join(name) not in self.namelist )

class NameLengthFilter:
    def __init__( self, min_length = 0, max_length = float("inf") ):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate( self, name ):
        return self.min_length <= len(name) <= self.max_length

class RegexFilter:
    def __init__( self, pattern ):
        assert type(pattern) == str
        import re
        self.regex = re.compile( pattern )
    
    def validate( self, name ):
        return self.regex.search( name ) != None
