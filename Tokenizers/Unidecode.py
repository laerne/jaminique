class UnidecodeTokenizer:

    def __init__( self,
            target_case = None,
            ):
        
        #load needed python module
        from unidecode import unidecode
        
        self.case_fct = None
        if target_case == "lower":
            self.decode_fct = lambda x: unidecode(x).lower()
        elif target_case == "upper":
            self.decode_fct = lambda x: unidecode(x).upper()
        else:
            self.decode_fct = unidecode

    def tokenize( self, name ):
        return tuple( self.decode_fct( name ) )

class SlugifyTokenizer:
    def __init__( self,
            target_case = "lower",
            separator = " ",
            ):

        #load needed python module
        from slugify import Slugify

        self.slug_ = Slugify(
            separator = separator,
            to_lower = ( target_case == "lower" ),
            )
            
    def tokenize( self, name ):
        return tuple( self.slug_( name ) )
