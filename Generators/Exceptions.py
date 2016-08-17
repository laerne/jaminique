class InvalidGeneratedWord(Exception):
    def __init__( self, message, word, weight ):
        self.message = message if message != None else "Partially generated word is invalid."
        self.word = word
        self.weight = weight
    def __str__( self ):
        return self.message


