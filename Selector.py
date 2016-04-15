import SmoothMarkov
import Markov
import Loader
import json
from copy import deepcopy

#TODO Deepcopy of some values
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
    #print( '<<<', dictionary1 )

class Arguments(object):
    def __init__( self, defaultArguments = {} ):
        self.args = deepcopy( defaultArguments )
    
    def update( self, other ):
        if type( other ) == dict:
            recursiveUpdate( self.args, other )
        elif type( other ) == Arguments:
            recursiveUpdate( self.args, other.args )
        elif type( other ) == str:
            data = json.loads( other )
            recursiveUpdate( self.args, data )
        elif hasattr( other, 'read' ):
            data = json.load( other )
            recursiveUpdate( self.args, data )
        else:
            raise Exception("Do not know how to update attributs with type %s" % (type(other)) )

    def get( self, *args, default=None ):
        current = self.args
        for a in args:
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
        
    def subArguments( self, *args ):
        data = self.get( *args, default={} )
        return Arguments( data )

    #Todo clean the tree when setting to 'None'
    def set( self, value, *args ):
        current = self.args
        args = list( args )
        n = len( args )
        
        if n == 0:
            self.args = value
            return
            
        while n > 0:
            a = args.pop(0)
            n = len( args )
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
                        current.add( a )
                    elif a in current:
                        current.remove( a )
                else:
                    raise Exception("Having to reach down non key-value type %s" % str(type( current )) )
                
            else:
                print( '???', current )
                raise Exception("Having to reach down unknown type %s" % str(type( current )) )
                
    def __str__( self ):
        return 'Arguments(' + str( self.args ) + ')'

    def __repr__( self ):
        return 'Arguments(' + repr(self.args) + ')'
            
        
        
#TODO read a json configuration file
def loadDefaultArguments():
    arguments = Arguments()
    with open( 'config.json', 'rt' ) as configfile:
        arguments.update( configfile )
    return arguments

def selectTokenizer( argumentDictionary, dictionary ):
    return None

#TODO receive a tokenized dictionary
def selectGenerator( argumentDictionary, dictionary ):
    args = loadDefaultArguments()
    args.update( argumentDictionary )
    
    algoName = args.get( "generator", "default", default="markov" )
    
    if algoName == "markov":
        generator = Markov.Generator( 
                dictionary,
                nGramLength = args.get('markov','ngram-size'),
                )

    elif algoName == "smooth-markov":
        generator = SmoothMarkov.Generator( 
                dictionary,
                minNGramLength = 0,
                maxNGramLength = args.get('smooth-markov','ngram-size'),
                generateDelimiterSymbols = True,
                )
    else:
        generator = None
    return generator

# Return a list of filter to discard some generated results
def selectFilters( argumentDictionary ):
    return []

def selectDictionaryTokenizerGeneratorFilters( argumentDictionary ):
    #Should be the tokenizer
    dictionary = Loader.loadDictionary(
            *argumentDictionary.get('dictionary','files'),
            uniformWeights = argumentDictionary.get('dictionary','uniform'),
            forceLowerCase = argumentDictionary.get('dictionary','ignore-case')
            )
    tokenizer = selectTokenizer( argumentDictionary.subArguments('tokenizer'), dictionary )
    generator = selectGenerator( argumentDictionary.subArguments('generator'), dictionary )
    filters = selectFilters( None )
    return dictionary, tokenizer, generator, filters

