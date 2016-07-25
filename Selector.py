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
import json
import MainTokenizers

from utilities import warn, fail, InvalidGeneratedWord

        
#TODO read a json configuration file
def loadDefaultArgumentTree():
    arguments = ArgumentTree()
    with open( 'config.json', 'rt' ) as configfile:
        arguments.update( configfile )
    return arguments

def argumentTreeUpdatedOnBase( initialArgumentsName, argumentsMap, recursive = True ):
    if initialArgumentsName not in argumentsMap:
        return ArgumentTree()

    currentArguments = argumentsMap[ initialArgumentsName ].clone()
    
    if not currentArguments.contains('base'):
        currentArguments.set( initialArgumentsName, '*base-name' )
        return currentArguments
    else:
        newArguments = None
        
        if recursive:
            newArguments = argumentTreeUpdatedOnBase( currentArguments.get('base'), argumentsMap )
        else:
            newArguments = argumentsMap[ currentArguments.get('base') ].clone()

        currentArguments.unset('base')
        newArguments.update( currentArguments )
        return newArguments

def selectSubTreeWithBase( arguments, *path ):
    pathToDefault = path + ('default',)
    targetName = arguments.get( *pathToDefault )
    
    def toSubTree( kv ):
        k, v = kv
        return ( k, ArgumentTree( v ) )
    cotargets = arguments.get( *path )
    argumentsMap = dict( map( toSubTree, cotargets.items() ) )
    
    
    targetArguments = argumentTreeUpdatedOnBase( targetName, argumentsMap )
    return targetName, targetArguments
    
        

def selectTokenizer( arguments, lexicon ):
    tokenizerName, tokenizerArguments = selectSubTreeWithBase( arguments, 'tokenizer' )
    tokenizerAlgorithm = tokenizerArguments.get( 'algorithm' ) or tokenizerArguments.get( '*base-name' )
    

    #Solve aliases
    if tokenizerAlgorithm == "unicode":
        tokenizerAlgorithm = "utf8"


    #Select algorithm
    if tokenizerAlgorithm == "utf8":
        tokenizer =  MainTokenizers.UnicodeTokenizer()
    elif tokenizerAlgorithm == "ll1":
        tokens = tokenizerArguments.get( 'token-list', default="" ).split(",")
        tokenizer =  MainTokenizers.LL1Tokenizer( tokens )
    else:
        tokenizer = None
        fail( 'No valid tokenizer with name %s' % repr(tokenizerAlgorithm) )
        
    
    #Notification for verbose mode
    if arguments.get('verbose'):
        print( 'Choosing tokenizer %s' % repr(tokenizerAlgorithm) )
    
    return tokenizer

#TODO receive a tokenized lexicon
def selectGenerator( arguments, lexicon ):
    generatorName, generatorArguments = selectSubTreeWithBase( arguments, 'generator' )
    generatorAlgorithm = generatorArguments.get( 'algorithm' ) or generatorArguments.get( '*base-name' )
    
    #Select algorithm
    if generatorAlgorithm == "markov":
        generator = Markov.Generator( 
                lexicon,
                nGramLength = generatorArguments.get( 'ngram-size', default=2 ),
                minNameLength = generatorArguments.get( 'min-length', default=0 ),
                maxNameLength = generatorArguments.get( 'truncation-length', default=256 ),
                #verbose = arguments.get('verbose'),
                )

    elif generatorAlgorithm == "smooth-markov":
        generator = SmoothMarkov.Generator( 
                lexicon,
                minNGramLength = 0,
                maxNGramLength = generatorArguments.get( 'ngram-size', default=2 ),
                minNameLength = generatorArguments.get( 'min-length', default=0 ),
                maxNameLength = generatorArguments.get( 'truncation-length', default=256 ),
                generateDelimiterSymbols = True,
                )
    else:
        generator = None
        fail( 'No valid generator with name %s' % repr(generatorAlgorithm) )

    #Notification for verbose mode
    if arguments.get('verbose'):
        print( 'Choosing generator %s' % repr(generatorAlgorithm) )
        
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
                
            
