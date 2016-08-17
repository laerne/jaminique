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

from ArgumentTree import ArgumentTree
import Loader
import Tokenizers
import Generators
import Filters
import json

from utilities import warn, fail
from utilities import DeterministicPicker, GeometricPicker, BinomialPicker, UniformPicker, GaussPicker

import appdirs
import os.path

#TODO: Have dictionary files relative to the configuration file not sys.argv[0]
def loadCoreConfiguration():
    from sys import argv
    config_path = os.path.join( os.path.dirname( argv[0] ), "config.json" )
    
    if os.path.isfile( config_path ):
        with open( config_path, 'rt' ) as configfile:
            return ArgumentTree( configfile )
    else:
       return ArgumentTree()

def loadSystemConfiguration():
    config_path = os.path.join( appdirs.site_config_dir( 'jaminique' ), "config.json" )
    
    if os.path.isfile( config_path ):
        with open( config_path, 'rt' ) as configfile:
            return ArgumentTree( configfile )
    else:
       return ArgumentTree()

def loadUserConfiguration():
    config_path = os.path.join( appdirs.user_config_dir( 'jaminique' ), "config.json" )
    
    if os.path.isfile( config_path ):
        with open( config_path, 'rt' ) as configfile:
            return ArgumentTree( configfile )
    else:
       return ArgumentTree()


def loadDefaultArgumentTree():
    cfg = ArgumentTree()
    cfg.update( loadCoreConfiguration() )
    cfg.update( loadSystemConfiguration() )
    cfg.update( loadUserConfiguration() )
    return cfg
    

def argumentTreeUpdatedOnBase( initialcfgName, cfgMap, recursive = True ):
    if initialcfgName not in cfgMap:
        return ArgumentTree()

    currentcfg = cfgMap[ initialcfgName ].clone()
    
    if not currentcfg.contains('base'):
        currentcfg.set( initialcfgName, '<base-name>' )
        return currentcfg
    else:
        newcfg = None
        
        if recursive:
            newcfg = argumentTreeUpdatedOnBase( currentcfg.get('base'), cfgMap )
        else:
            newcfg = cfgMap[ currentcfg.get('base') ].clone()

        currentcfg.unset('base')
        newcfg.update( currentcfg )
        return newcfg

def selectSubTreeWithBase( cfg, *path ):
    pathToDefault = path + ('default',)
    targetName = cfg.get( *pathToDefault )
    
    def toSubTree( kv ):
        k, v = kv
        return ( k, ArgumentTree( v ) )
    ##TODO change the cotarget path to go under a "presets" tag
    #cotargets = dict( cfg.get( *path ) )
    #del cotargets['default']
    pathToPresets = path + ('presets',)
    presets = cfg.get( *pathToPresets )
    cfgMap = dict( map( toSubTree, presets.items() ) )
    
    
    targetcfg = argumentTreeUpdatedOnBase( targetName, cfgMap )
    return targetName, targetcfg
    
        

def selectTokenizer( cfg, lexicon ):
    tokenizerName, tokenizercfg = selectSubTreeWithBase( cfg, 'tokenizer' )
    tokenizerAlgorithm = tokenizercfg.get( 'algorithm' ) or tokenizercfg.get( '<base-name>' )
    

    #Solve aliases
    if tokenizerAlgorithm == "unicode":
        tokenizerAlgorithm = "utf8"


    #Select algorithm
    if tokenizerAlgorithm == "utf8":
        tokenizer =  Tokenizers.UnicodeTokenizer(
            target_case = tokenizercfg.get( 'case' ),
            )
    elif tokenizerAlgorithm == "ll1":
        tokens = tokenizercfg.get( 'token-list', default="" ).split(",")
        tokenizer =  Tokenizers.LL1Tokenizer( tokens )
    elif tokenizerAlgorithm == "unidecode":
        tokenizer = Tokenizers.UnidecodeTokenizer(
            target_case = tokenizercfg.get( 'case' ),
            )
    elif tokenizerAlgorithm == "slugify":
        tokenizer = Tokenizers.SlugifyTokenizer(
            separator = tokenizercfg.get( 'separator', default=" " ),
            target_case = tokenizercfg.get( 'case' ),
            )
    else:
        tokenizer = None
        raise InvalidTokenizerName( name = tokenizerAlgorithm )
        
    
    #Notification for verbose mode
    if cfg.get('verbose'):
        print( 'Choosing tokenizer %s using settings %s' % (repr(tokenizerAlgorithm),repr(tokenizerName)) )
    
    return tokenizer

#TODO receive a tokenized lexicon
def selectGenerator( cfg, lexicon ):
    generatorName, generatorcfg = selectSubTreeWithBase( cfg, 'generator' )
    generatorAlgorithm = generatorcfg.get( 'algorithm' ) or generatorcfg.get( '<base-name>' )
    
    #Select algorithm
    if generatorAlgorithm == "markov":
        generator = Generators.MarkovGenerator( 
                lexicon,
                nGramLength = generatorcfg.get( 'ngram-size', default=2 ),
                minNameLength = generatorcfg.get( 'min-length', default=0 ),
                maxNameLength = generatorcfg.get( 'truncation-length', default=256 ),
                #verbose = cfg.get('verbose'),
                )

    elif generatorAlgorithm == "smooth-markov":
        generator = Generators.SmoothMarkovGenerator( 
                lexicon,
                minNGramLength = 0,
                maxNGramLength = generatorcfg.get( 'ngram-size', default=2 ),
                minNameLength = generatorcfg.get( 'min-length', default=0 ),
                maxNameLength = generatorcfg.get( 'truncation-length', default=256 ),
                generateDelimiterSymbols = True,
                )
    elif generatorAlgorithm == "portmanteau":
        generator = Generators.PortmanteauGenerator( 
                lexicon,
                length_rv = DeterministicPicker( value = generatorcfg.get('size') ),
                )
    else:
        generator = None
        raise InvalidGeneratorName( name = generatorAlgorithm )

    #Notification for verbose mode
    if cfg.get('verbose'):
        print( 'Choosing generator %s using settings %s' % (repr(generatorAlgorithm),repr(generatorName)) )
        
    return generator

# Return a list of filter to discard some generated results
def selectFilters( cfg, lexicon ):
    filtersPresetName, filtersCfg = selectSubTreeWithBase( cfg, 'filters' )

    filters = []

    #OriginalOnlyFilter
    if filtersCfg.get( 'original' ) == True:
        filters.append(   Filters.OriginalOnlyFilter( lexicon )   )

    #NameLengthFilter
    minLength = filtersCfg.get( 'min-length', default=0 )
    maxLength = filtersCfg.get( 'max-length', default=float("inf") )
    if minLength > 0 or maxLength < float("inf"):
        filters.append(   Filters.NameLengthFilter( minLength, maxLength )   )
        
    if filtersCfg.contains( 'regex' ):
        pattern = filtersCfg.get( 'regex' )
        filters.append( Filters.RegexFilter( pattern ) )

    if cfg.get('verbose'):
        print( 'Choosing filters using settings %s' % (repr(filtersPresetName)) )

    return Filters.AggregateFilter( filters )
    

def selectLexiconTokenizerGeneratorFilters( cfg ):
    #TODO cache small lexicons in memory
    files = cfg.get('lexicon','*selected_files') or cfg.get('lexicon','files') or []
    if cfg.get('lexicon','use_patterns',default=True):
        lexicon = Loader.loadLexiconsFromPatterns( files )
    else:
        lexicon = Loader.loadLexicons( files )

    if len( lexicon ) == 0:
        raise EmptyLexicon()

    tokenizer = selectTokenizer( cfg, lexicon )
    def to_token_sequence( keyval ):
        return tokenizer.tokenize( keyval[0] ), keyval[1]
    tokenized_lexicon = dict( map( to_token_sequence , lexicon.items() ) )

    generator = selectGenerator( cfg, tokenized_lexicon )
    filters = selectFilters( cfg, lexicon )
    return lexicon, tokenizer, generator, filters

def generate( cfg ):
    lexicon, tokenizer, generator, filters = selectLexiconTokenizerGeneratorFilters( cfg )

    number_to_generate = cfg.get('number', default=1)
    max_loops = cfg.get( 'infinity-threshold', default=65535 )
    for i in range(number_to_generate):
    
        has_generated_a_valid_name = False
        
        for j in range( max_loops ):
            weight, name = 0.0, ""
            try:
                weight, name = generator.generateName()
            except Generators.InvalidGeneratedWord as e:
                if cfg.get( 'verbose', default=False ):
                    try:
                        print("%.4f <!> %s <!> %s" % (e.weight, e.word, str(e) ) )
                    except UnicodeError:
                        print("%.4f <!> %s <!> %s" % (e.weight, e.word, str(e).encode('ascii','hreplace').decode('ascii') ) )
                continue
            
            valid = filters.validate( name )
            
            if cfg.get('verbose'):
                validitySymbol = "(+)" if valid else "(-)"
                try:
                    print("%.4f %s %s" % (weight, validitySymbol, name) )
                except UnicodeError:
                    print("%.4f %s %s" % (weight, validitySymbol, name.encode('ascii','replace').decode('ascii')) )

            if valid:
                yield weight, name
                has_generated_a_valid_name = True
                break
                
        if not has_generated_a_valid_name:
            raise TooManyIterations(
                    message = "Could not generate valid name in less than %d attempts" % max_loops,
                    nb_iterations = max_loops,
                    )
            break
                
            
class InvalidAlgorithmName(Exception):
    def __init__( self, name, message = None ):
        self.name = name
        
        if message == None:
            message = "Invalid algorithm name %s." % repr(name)
        super(InvalidAlgorithmName,self).__init__( message )

class InvalidTokenizerName(InvalidAlgorithmName):
    def __init__( self, name, message = None ):
        if message == None:
            message = "Invalid tokenizer algorithm name %s." % repr(name)
        super(InvalidTokenizerName,self).__init__( name, message )

class InvalidGeneratorName(InvalidAlgorithmName):
    def __init__( self, name, message = None ):
        if message == None:
            message = "Invalid generator algorithm name %s." % repr(name)
        super(InvalidGeneratorName,self).__init__( name, message )

class TooManyIterations(Exception):
    def __init__( self, nb_iterations, message = None ):
        self.nb_iterations = nb_iterations
        
        if message == None:
            self.message = "Reached the iteration ceiling '%d'." % nb_iterations
        super(TooManyIterations,self).__init__( message )

class EmptyLexicon(Exception):
    def __init__( self ):
        super(EmptyLexicon,self).__init__( "Cannot generate a word from an empty lexicon" )
