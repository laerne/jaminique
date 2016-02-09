#/usr/bin/env python3

def writeDictionary( filepath, dictionary ):
    writeDictionaryFromIterator( filepath, dictionary.values() )
            
def writeDictionaryFromIterator( filepath, dictionaryIterator ):
    with open( filepath, 'wt' ) as outputStream:
        for word, perplexity in dictionaryIterator:
            outputStream.write( word + '\n' )
