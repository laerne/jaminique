#/usr/bin/env python3
from gi import require_version
require_version('Gtk','3.0')
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
    
    def on_add_dictionary( self, button ):
        dictionary_data = self.stores["dictionaries"]
        dialog = Gtk.FileChooserDialog(
                "Open SVG file",
                None,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                )
        dialog.set_select_multiple(True)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():
                cachedDictionary = Loader.loadDictionary( filename )
                
                name = os.path.splitext( os.path.basename( filename ) )[0]
                wordcount = len( cachedDictionary )
                weightcount = sum( cachedDictionary.values() )
                
                dictionary_data.append( None, (filename,wordcount,weightcount,name,True) )
                self.dictionaries[ filename ] = cachedDictionary
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True
    
    def on_remove_dictionary( self, selection ):
        dictionary_data, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: dictionary_data.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            dictionary_data.remove( row_iter )
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
    prefixCounter = PrefixCounter.PrefixCounter( dictionary, generateDelimiterSymbols=True )
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
