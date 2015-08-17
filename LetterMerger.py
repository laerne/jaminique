#/usr/bin/env python3
import DictionaryBuilder as db

def guessArticulations( dictionary ):
    followingCharCounter = db.buildPrefixCounters( dictionary, minlen = 1, maxlen = 1, generateDelimiterSymbols = False )[1]
    

if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser(
            usage='%(prog)s [options] dictionary [dictionary...]',
            description='Build letter groups of a language.',
            )

    argparser.add_argument( 'dictionary', action='store', nargs='*',
            default=['namelists/viking_male.txt','namelists/viking_female.txt','namelists/viking_unknownGender.txt'],
            help='Dictionary of name to learn from.' )

    args = argparser.parse_args()
    


    dictionary = db.loadDictionary( *args.dictionary )
    guessArticulations( dictionary )

