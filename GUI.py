import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import os.path
from sys import argv

import PrefixCounter
import Generator
import Loader

glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )

class GUIHandler(object):
    def __init__( self, windows, stores ):
        self.windows = windows
        self.stores = stores
        self.dictionaries = {}
        
    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True
    
    def on_add_dictionary( self, dialog ):
        dialog.show()
        return True
    
    def on_remove_dictionary( self, selection ):
        dictionary_data, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: dictionary_data.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            dictionary_data.remove( row_iter )
        return True

    def on_delete_dictfile_chooser_dialog( self, dialog, eventType ):
        dialog.hide()
        return True
    
    def on_dictfile_chooser_close_button_clicked( self, dialog ):
        dialog.hide()
        return True
    
    def on_dictfile_chooser_add_button_clicked( self, dialog ):
        dictionary_data = self.stores["dictionaries"]

        for uri in dialog.get_uris():
            assert uri[:7] == "file://"
            filepath = uri[7:]
            cachedDictionary = Loader.loadDictionary( filepath )
            
            name = os.path.splitext( os.path.basename( filepath ) )[0]
            wordcount = len( cachedDictionary )
            weightcount = sum( cachedDictionary.values() )
            
            dictionary_data.append( None, (filepath,wordcount,weightcount,name,True) )
            self.dictionaries[ filepath ] = cachedDictionary
            
        dialog.hide()
        return True
    
    def on_is_used_selector_toggled( self, toggleButton, row_path ):
        dictionary_data = self.stores["dictionaries"]
        row_iter = dictionary_data.get_iter( row_path )
        former_value = dictionary_data.get_value( row_iter, 4 )
        dictionary_data.set( row_iter, [4], [not former_value] )
        return True
    
    def foreach_dictionary_data( self, model, path, iter, accumulator ):
        is_used = model.get_value( iter, 4 )
        filepath = model.get_value( iter, 0 )
        if is_used:
            Loader.mergeDictionary( accumulator, self.dictionaries[filepath] )
    
    def on_generate_button_clicked( self, button ):
        merged = {}
        self.stores["dictionaries"].foreach( self.foreach_dictionary_data, merged )
        
        if len(merged) == 0:
            print("Nothing to generate from")
            return True
        
        for perpexity, name in simpleLangrangeGenerate( merged, 1 ):
            self.stores["generated_names"].append((name,perpexity))
        
        return True
    

def simpleLangrangeGenerate( dictionary, numberOfGenerations ):
    prefixCounter = PrefixCounter.PrefixCounter( dictionary )
    generator = Generator.SimpleLagrangeGenerator( prefixCounter )
    
    n = 0
    while n < numberOfGenerations:
        namePerplexity, name = generator.generateName()
        yield (namePerplexity, name)
        n +=1

def runGUI():
    glade_path = os.path.join( glade_prefix, "main_ui.glade" )
    builder = Gtk.Builder.new_from_file( glade_path )
    
    window_ids = ["main_window","dictfile_chooser"]
    windows = dict(map(   lambda wid: (wid,builder.get_object(wid)),   window_ids   ))
    store_ids = ["dictionaries","generated_names", "generation_algorithms"]
    stores = dict(map(   lambda wid: (wid,builder.get_object(wid)),   store_ids   ))
    
    builder.connect_signals( GUIHandler(windows,stores) )
    windows["main_window"].show_all()
    
    Gtk.main()

if __name__ == '__main__':
    runGUI()
