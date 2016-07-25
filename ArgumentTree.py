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

from copy import deepcopy
import json

def recursiveUpdate( dictionary1, dictionary2 ):
    #print( '>>>', dictionary1 )
    #print( '+++', dictionary2 )
    for key in dictionary2.keys():
        if key not in dictionary1:
            dictionary1[ key ] = dictionary2[ key ]
        else:
            value1 = dictionary1[ key ]
            value2 = dictionary2[ key ]
            if type( value1 ) == type( value2 ) == dict:
                recursiveUpdate( value1, value2 )
            elif type( value1 ) == set and type( value2 ) in {set,frozenset}:
                dictionary1[ key ].update( value2 )
            elif type( value1 ) == frozenset and type( value2 ) in {set,frozenset}:
                dictionary1[ key ] = value1 | frozenset( value2 )
            elif type( value1 ) == type( value2 ) == list:
                dictionary1[ key ] = value2
            else:
                dictionary1[ key ] = value2

class ArgumentTree(object):
    def __init__( self, defaultArgumentTree = {} ):
        self.args = deepcopy( defaultArgumentTree )
    
    def update( self, other ):
        if type( other ) == dict:
            recursiveUpdate( self.args, other )
        elif type( other ) == ArgumentTree:
            recursiveUpdate( self.args, other.args )
        elif type( other ) == str:
            data = json.loads( other )
            recursiveUpdate( self.args, data )
        elif hasattr( other, 'read' ):
            data = json.load( other )
            recursiveUpdate( self.args, data )
        else:
            raise Exception("Do not know how to update attributs with type %s" % (type(other)) )

    def get( self, *path, default=None ):
        current = self.args
        for a in path:
            if type( current ) == list:
                if type( a ) != int or a < 0 or a >= len( current ):
                    return default
                current = current[ a ]
            elif type( current ) == dict:
                if a not in current:
                    return default
                current = current[ a ]
            elif type( current ) == set or type( current ) == frozenset:
                current = ( a in current ) #Necesseraly True or False
            else:
                return default
        return current
    
    def contains( self, *path ):
        class TOKEN:
            pass
        return self.get( *path, default=TOKEN ) != TOKEN
        
    def subArgumentTree( self, *path ):
        data = self.get( *path, default={} )
        return ArgumentTree( data )
    #Todo clean the tree when setting to 'None'
    def set( self, value, *path ):
        current = self.args
        path = list( path )
        n = len( path )
        
        if n == 0:
            self.args = value
            return
            
        while n > 0:
            a = path.pop(0)
            n = len( path )
            #c = current if type(current) != dict else set( current.keys() )
            #print( '!!!', "n:%d"%n, "a:%s"%repr(a), "c:%s"%repr(c), "v:%s"%repr(value) )
                
            if type( current ) == list:
                if type( a ) != int or a < 0 or a >= len( current ):
                    raise Exception("Having to reach down a list with an invalid subscript.")

                if n == 0:
                    if value != None:
                        current[ a ] = value
                current = current[ a ]
                
            elif type( current ) == dict:
                if n == 0:
                    current[ a ] = value
                elif a not in current:
                    current[ a ] = {}
                    current = current[ a ]
                else:
                    current = current[ a ]
                
            elif type( current ) == set or type( current ) == frozenset:
                if n == 0:
                    if value:
                        current |= {a}
                    elif a in current:
                        current -= {a}
                else:
                    raise Exception("Having to reach down non key-value type %s" % str(type( current )) )
                
            else:
                print( '???', current )
                raise Exception("Having to reach down unknown type %s" % str(type( current )) )

    def unset( self, *path ):
        current = self.args
        path = list( path )
        n = len( path )
        
        if n == 0:
            self.args = {}
            return
            
        while n > 0:
            a = path.pop(0)
            n = len( path )
                
            if type( current ) == list:
                if type( a ) != int or a < 0 or a >= len( current ):
                    raise Exception("Having to reach down a list with an invalid subscript.")

                if n == 0:
                    del current[ a ]
                current = current[ a ]
                
            elif type( current ) == dict:
                if n == 0:
                    del current[ a ]
                elif a not in current:
                    raise Exception("Having to reach down a dict without key \"%s\"." % str(a) )
                else:
                    current = current[ a ]
                
            elif type( current ) == set or type( current ) == frozenset:
                if n == 0:
                    current -= {a}
                else:
                    raise Exception("Having to reach down non key-value type %s" % str(type( current )) )
                
            else:
                print( '???', current )
                raise Exception("Having to reach down unknown type %s" % str(type( current )) )

    def clone( self ):
        from copy import deepcopy
        return ArgumentTree( deepcopy( self.args ) )
                
    def __str__( self ):
        return 'ArgumentTree(' + str( self.args ) + ')'

    def __repr__( self ):
        return 'ArgumentTree(' + repr(self.args) + ')'

