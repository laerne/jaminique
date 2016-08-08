class UnicodeTokenizer:
    def tokenize( self, name ):
        return tuple( name )

class UniformCaseTokenizer:
    def __init__( self, target_case = "lower" ):
        if target_case == "upper":
            self.case_fct = str.upper
        elif target_case == "lower":
            self.case_fct = str.lower
        else:
            self.case_fct = str.lower
            
    def tokenize( self, name ): 
        return tuple( self.case_fct(name) )
        
class LL1Tokenizer:
    def __init__( self, tokens ):
        lengths = sorted( set( map( len, tokens ) ), reverse = True )
        if lengths[-1] == 0:
          #Discard invalid tokens such as "", but keep order
          del lengths[-1]

        sortedTokens = []
        for l in lengths:
          sortedTokens += sorted( [ token for token in tokens if len(token) == l ] )
        
        self.tokens_ = tokens
    
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
            else:
                pass
              

        return tuple( result )
        
