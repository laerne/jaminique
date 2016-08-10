class UnidecodeTokenizer:

    def __init__( self,
            target_case = None,
            ):
        
        #load needed python module
        from unidecode import unidecode
        self.decode_fct = unidecode
        
        self.case_fct = None
        if target_case == "lower":
            self.case_fct = str.lower
        elif target_case == "upper":
            self.case_fct = str.upper

    def tokenize( self, name ):
        return tuple( self.case_fct( self.decode_fct( name ) ) )

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
