class UnicodeTokenizer:
    def tokenize( self, name ):
        return tuple( name )

class LL1Tokenizer:
    def __init__( self, sorted_tokens ):
        self.tokens_ = sorted_tokens
    
    #Defaults to UnicodeTokenizer if no token can be found
    def tokenize( self, name ):
        result = []
        while len(name) > 0:
            hasMatch = False
            for token in self.tokens_:
                if name.startswith(token):
                    result.append( token )
                    name = name[ len(token): ]
                    hasMatch=True
                    break
            if not hasMatch:
                result.append( name[0] )
                name = name[1:]
                hasMatch=True

        return tuple( result )
        
