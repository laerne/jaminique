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
import MainFilters
import Markov
import SmoothMarkov
import CompoundWord
import json
import MainTokenizers

from utilities import warn, fail, InvalidGeneratedWord
from utilities import DeterministicPicker, GeometricPicker, BinomialPicker, UniformPicker, GaussPicker

import appdirs
import os.path

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
        currentcfg.set( initialcfgName, '*base-name' )
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
    tokenizerAlgorithm = tokenizercfg.get( 'algorithm' ) or tokenizercfg.get( '*base-name' )
    

    #Solve aliases
    if tokenizerAlgorithm == "unicode":
        tokenizerAlgorithm = "utf8"


    #Select algorithm
    if tokenizerAlgorithm == "utf8":
        tokenizer =  MainTokenizers.UnicodeTokenizer()
    elif tokenizerAlgorithm == "ll1":
        tokens = tokenizercfg.get( 'token-list', default="" ).split(",")
        tokenizer =  MainTokenizers.LL1Tokenizer( tokens )
    else:
        tokenizer = None
        fail( 'No valid tokenizer with name %s' % repr(tokenizerAlgorithm) )
        
    
    #Notification for verbose mode
    if cfg.get('verbose'):
        print( 'Choosing tokenizer %s using settings %s' % (repr(tokenizerAlgorithm),repr(tokenizerName)) )
    
    return tokenizer

#TODO receive a tokenized lexicon
def selectGenerator( cfg, lexicon ):
    generatorName, generatorcfg = selectSubTreeWithBase( cfg, 'generator' )
    generatorAlgorithm = generatorcfg.get( 'algorithm' ) or generatorcfg.get( '*base-name' )
    
    #Select algorithm
    if generatorAlgorithm == "markov":
        generator = Markov.Generator( 
                lexicon,
                nGramLength = generatorcfg.get( 'ngram-size', default=2 ),
                minNameLength = generatorcfg.get( 'min-length', default=0 ),
                maxNameLength = generatorcfg.get( 'truncation-length', default=256 ),
                #verbose = cfg.get('verbose'),
                )

    elif generatorAlgorithm == "smooth-markov":
        generator = SmoothMarkov.Generator( 
                lexicon,
                minNGramLength = 0,
                maxNGramLength = generatorcfg.get( 'ngram-size', default=2 ),
                minNameLength = generatorcfg.get( 'min-length', default=0 ),
                maxNameLength = generatorcfg.get( 'truncation-length', default=256 ),
                generateDelimiterSymbols = True,
                )
    elif generatorAlgorithm == "portmanteau":
        generator = CompoundWord.Generator( 
                lexicon,
                length_rv = DeterministicPicker( value = generatorcfg.get('size') ),
                )
    else:
        generator = None
        fail( 'No valid generator with name %s' % repr(generatorAlgorithm) )

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
        filters.append(   MainFilters.OriginalOnlyFilter( lexicon )   )

    #NameLengthFilter
    minLength = filtersCfg.get( 'min-length', default=0 )
    maxLength = filtersCfg.get( 'max-length', default=float("inf") )
    if minLength > 0 or maxLength < float("inf"):
        filters.append(   MainFilters.NameLengthFilter( minLength, maxLength )   )
        
    if filtersCfg.contains( 'regex' ):
        pattern = filtersCfg.get( 'regex' )
        filters.append( MainFilters.RegexFilter( pattern ) )

    if cfg.get('verbose'):
        print( 'Choosing filters using settings %s' % (repr(filtersPresetName)) )

    return MainFilters.AggregateFilter( filters )
    

def selectLexiconTokenizerGeneratorFilters( cfg ):
    lexicon = cfg.get('*cached-lexicon', default=None )
    if lexicon == None:
        files = cfg.get('lexicon','*selected_files') or cfg.get('lexicon','files') or []
        lexicon = Loader.loadLexicon(
                *files,
                uniformWeights = cfg.get('lexicon','uniform'),
                forceLowerCase = cfg.get('lexicon','ignore-case')
                )

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
            except InvalidGeneratedWord as e:
                if cfg.get( 'verbose', default=False ):
                    print("%.4f <!> %s <!> %s" % (e.weight, e.word, str(e) ) )
                continue
            
            valid = filters.validate( name )
            
            if cfg.get('verbose'):
                validitySymbol = "(+)" if valid else "(-)"
                print("%.4f %s %s" % (weight, validitySymbol, name) )

            if valid:
                yield weight, name
                has_generated_a_valid_name = True
                break
                
        if not has_generated_a_valid_name:
            fail( "Could not generate valid name in less than %d attempts" % max_loops )
            break
                
            
