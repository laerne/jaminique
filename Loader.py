import fileinput

def loadDictionary( *filepaths, weightTransformationFct=(lambda x: x) ):
    dictionary = {}
    for line in fileinput.input( filepaths ):
        item = line.split('#')[0].strip()
        tokens = item.split(':')
        word = tokens[0]
        if word == '':
            continue
        weight = weightTransformationFct( tokens[1] if len( tokens ) > 2 else 1 )
        if word in dictionary:
            dictionary[word] += weight
        else:
            dictionary[word] = weight
    return dictionary


def mergeDictionaries( *dictionaries ):
    merged = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if key in merged:
                merged[key] += value
            else:
                merged[key] = value
    return merged
    
def mergeDictionary( editedDictionary, appendedDictionary ):
    for key, value in appendedDictionary.items():
        if key in editedDictionary:
            editedDictionary[key] += value
        else:
            editedDictionary[key] = value
    return editedDictionary
