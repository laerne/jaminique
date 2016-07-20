import Loader
import MainFilters
import Markov
import SmoothMarkov
import json
import MainTokenizers
from copy import deepcopy
from utilities import warn, fail, InvalidGeneratedWord

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
    
    def contains( self, *args ):
        class TOKEN:
            pass
        return self.get( *args, default=TOKEN ) != TOKEN
        
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
                        current |= {a}
                    elif a in current:
                        current -= {a}
                else:
                    raise Exception("Having to reach down non key-value type %s" % str(type( current )) )
                
            else:
                print( '???', current )
                raise Exception("Having to reach down unknown type %s" % str(type( current )) )

    def unset( self, *args ):
        current = self.args
        args = list( args )
        n = len( args )
        
        if n == 0:
            self.args = {}
            return
            
        while n > 0:
            a = args.pop(0)
            n = len( args )
                
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
        return Arguments( deepcopy( self.args ) )
                
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

def selectTokenizer( arguments, lexicon ):
    tokenizerName = arguments.get( 'default', default="unicode" )
    
    if tokenizerName == "unicode" or tokenizerName == "utf8":
        tokenizer =  MainTokenizers.UnicodeTokenizer()
    else:
        tokenizer = None
        fail( 'No valid tokenizer with name "%s"' % (tokenizerName), verbose = arguments.get('verbose') )
        
    
    if arguments.get('verbose'):
        print( 'Choosing tokenizer "%s"' % (tokenizerName) )
    
    return tokenizer

#TODO receive a tokenized lexicon
def selectGenerator( arguments, lexicon ):
    generatorName = arguments.get( 'generator', 'default', default="markov" )
    
    if generatorName == "markov":
        generator = Markov.Generator( 
                lexicon,
                nGramLength = arguments.get('generator', 'markov','ngram-size', default=2 ),
                minNameLength = arguments.get('generator', 'markov', 'min-length', default=0 ),
                maxNameLength = arguments.get('generator', 'markov', 'truncation-length', default=256 ),
                #verbose = arguments.get('verbose'),
                )

    elif generatorName == "smooth-markov":
        generator = SmoothMarkov.Generator( 
                lexicon,
                minNGramLength = 0,
                maxNGramLength = arguments.get( 'generator', 'smooth-markov', 'ngram-size', default=2 ),
                minNameLength = arguments.get( 'generator', 'smooth-markov', 'min-length', default=0 ),
                maxNameLength = arguments.get( 'generator', 'smooth-markov', 'truncation-length', default=256 ),
                generateDelimiterSymbols = True,
                )
    else:
        generator = None
        fail( 'No valid generator with name "%s"' % (generatorName), verbose = arguments.get('verbose') )

    if arguments.get('verbose'):
        print( 'Choosing generator "%s"' % (generatorName) )
        
    return generator

# Return a list of filter to discard some generated results
def selectFilters( arguments, lexicon ):

    filters = []

    #OriginalOnlyFilter
    if arguments.get( 'filters', 'original' ) == True:
        filters.append(   MainFilters.OriginalOnlyFilter( lexicon )   )

    #NameLengthFilter
    minLength = arguments.get( 'filters', 'min-length', default=0 )
    maxLength = arguments.get( 'filters', 'max-length', default=float("inf") )
    if minLength > 0 or maxLength < float("inf"):
        filters.append(   MainFilters.NameLengthFilter( minLength, maxLength )   )
        
    if arguments.contains( 'filters', 'regex' ):
        pattern = arguments.get( 'filters', 'regex' )
        filters.append( MainFilters.RegexFilter( pattern ) )

    return MainFilters.AggregateFilter( filters )
    

def selectLexiconTokenizerGeneratorFilters( arguments ):
    lexicon = arguments.get('*cached-lexicon', default=None )
    if lexicon == None:
        files = arguments.get('lexicon','*selected_files') or arguments.get('lexicon','files') or []
        lexicon = Loader.loadLexicon(
                *files,
                uniformWeights = arguments.get('lexicon','uniform'),
                forceLowerCase = arguments.get('lexicon','ignore-case')
                )

    tokenizer = selectTokenizer( arguments, lexicon )
    def to_token_sequence( keyval ):
        return tokenizer.tokenize( keyval[0] ), keyval[1]
    tokenized_lexicon = dict( map( to_token_sequence , lexicon.items() ) )

    generator = selectGenerator( arguments, tokenized_lexicon )
    filters = selectFilters( arguments, lexicon )
    return lexicon, tokenizer, generator, filters

def generate( arguments ):
    lexicon, tokenizer, generator, filters = selectLexiconTokenizerGeneratorFilters( arguments )

    number_to_generate = arguments.get('number', default=1)
    max_loops = arguments.get( 'infinity-threshold', default=65535 )
    for i in range(number_to_generate):
    
        has_generated_a_valid_name = False
        
        for j in range( max_loops ):
            weight, name = 0.0, ""
            try:
                weight, name = generator.generateName()
            except InvalidGeneratedWord as e:
                if arguments.get( 'verbose', default=False ):
                    print("%.4f <!> %s <!> %s" % (e.weight, e.word, str(e) ) )
                continue
            
            valid = filters.validate( name )
            
            if arguments.get('verbose'):
                validitySymbol = "(+)" if valid else "(-)"
                print("%.4f %s %s" % (weight, validitySymbol, name) )

            if valid:
                yield weight, name
                has_generated_a_valid_name = True
                break
                
        if not has_generated_a_valid_name:
            fail( "Could not generate valid name in less than %d attempts" % max_loops )
            break
                
            
