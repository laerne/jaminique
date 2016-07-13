#/usr/bin/env python3

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

import Selector

#TODO: CLI only parses options, when running without a gui, switch to this file

def process( arguments ):
    dictionary, tokenizer, generator, filters = Selector.selectDictionaryTokenizerGeneratorFilters( arguments )

    n = 0
    while n < arguments.get('number',default=1):
        namePerplexity, name = generator.generateName()
        if not filters.validate( name ):
            if arguments.get('verbose'):
                print("%.6f (!) %s" % (namePerplexity, name) )
            continue
        if arguments.get('verbose'):
            print("%.6f (+) %s" % (namePerplexity, name) )
        else:
            print("%s" % name )
        n +=1

