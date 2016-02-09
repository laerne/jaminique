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

from gi import require_version
require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import os.path
from sys import argv
from glob import iglob

import PrefixCounter
import Generator
import Loader
import Writer
from utilities import warn, fail

glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )

class GUIHandler(object):
    def __init__( self, windows, stores, inputs ):
        self.windows = windows
        self.stores = stores
        self.inputs = inputs
        self.dictionaries = {}
        
    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True
        
    def load_dictionary( self, filepath ):
        dictionary_data = self.stores["dictionaries"]
        cachedDictionary = Loader.loadDictionary( filepath )
        
        name = os.path.splitext( os.path.basename( filepath ) )[0]
        wordcount = len( cachedDictionary )
        weightcount = sum( cachedDictionary.values() )
        
        dictionary_data.append( None, (filepath,wordcount,weightcount,name,True) )
        self.dictionaries[ filepath ] = cachedDictionary
            
        
    def on_add_dictionary( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Open dictionary file",
                self.windows["main_window"],
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                )
        dialog.set_select_multiple(True)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():
                self.load_dictionary( filename )
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

    def on_toggle_select_all_dictionaries( self, selection ):
        used_dictionaries_filter_list = []
        def test_if_at_least_one_dictionary_is_used( model, path, iter, accumulator ):
            is_used = model.get_value( iter, 4 )
            name = model.get_value( iter, 3 )
            if is_used:
                accumulator.append( name )
        self.stores["dictionaries"].foreach( test_if_at_least_one_dictionary_is_used, used_dictionaries_filter_list )
        
        def update_used_dictionaries( model, path, iter, new_status ):
            model.set_value( iter, 4, new_status )
        if len(used_dictionaries_filter_list) > 0:
            self.stores["dictionaries"].foreach( update_used_dictionaries, False )
        else:
            self.stores["dictionaries"].foreach( update_used_dictionaries, True )
    
    
    def on_generate_button_clicked( self, button ):
        merged = {}
        def foreach_dictionary_data( model, path, iter, accumulator ):
            is_used = model.get_value( iter, 4 )
            filepath = model.get_value( iter, 0 )
            if is_used:
                Loader.mergeDictionary( accumulator, self.dictionaries[filepath] )
        self.stores["dictionaries"].foreach( foreach_dictionary_data, merged )
        
        if len(merged) == 0:
            print("Nothing to generate from")
            return True
        
        numberOfGenerations = self.inputs["number_to_generate_spinner"].get_value_as_int()
        for perpexity, name in simpleLangrangeGenerate( merged, numberOfGenerations ):
            self.stores["generated_names"].append((name,perpexity))
        
        return True

    def on_entry_perplexity_edited( self, cell, iterstring, value  ):
        names_store = self.stores["generated_names"]
        iter = names_store.get_iter( iterstring )
        names_store.set_value( iter, 1, value )
        
    def on_entry_name_edited( self, cell, iterstring, value  ):
        names_store = self.stores["generated_names"]
        iter = names_store.get_iter( iterstring )
        names_store.set_value( iter, 0, value )
        names_store.set_value( iter, 1, 0.0 )
        
    def on_add_entry( self, selection ):
        names_store, row_paths =  selection.get_selected_rows()
        if len(row_paths) == 0:
            names_store.append(("",0.0))
        else:
            should_be_last_iter = names_store.get_iter( row_paths[-1] )
            names_store.insert_after( should_be_last_iter, ("",0.0) )
        return True

    def on_remove_entry( self, selection ):
        names_store, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: names_store.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            names_store.remove( row_iter )
        return True
        
    def on_remove_all_entries( self, selection ):
        self.stores["generated_names"].clear()
        return True
        
    def on_save_entries( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Save generated names",
                self.windows["main_window"],
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT),
                )
                
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            def store_iterator():
                names_store = self.stores["generated_names"]
                for row in names_store:
                    yield( row[0], row[1] )
            Writer.writeDictionaryFromIterator( filename, store_iterator() )
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True
    

def simpleLangrangeGenerate( dictionary, numberOfGenerations ):
    prefixCounter = PrefixCounter.PrefixCounter( dictionary, generateDelimiterSymbols=True )
    generator = Generator.SimpleLagrangeGenerator( prefixCounter )
    
    n = 0
    while n < numberOfGenerations:
        namePerplexity, name = generator.generateName()
        yield (namePerplexity, name)
        n +=1

def preloadNamelists( gui_handler, namelists_folder = None ):
    if namelists_folder == None:
        namelists_folder = os.path.join( os.path.dirname( argv[0] ), "namelists" )
    namelists_folder = os.path.abspath( namelists_folder )
    print( namelists_folder )
    for filepath in iglob( os.path.join( namelists_folder, "*.txt" ) ):
        gui_handler.load_dictionary(filepath)
    

def runGUI():
    glade_path = os.path.join( glade_prefix, "main_ui.glade" )
    builder = Gtk.Builder.new_from_file( glade_path )
    
    window_ids = ["main_window","dictfile_chooser"]
    windows = dict(map(   lambda wid: (wid,builder.get_object(wid)),   window_ids   ))
    store_ids = ["dictionaries","generated_names", "generation_algorithms"]
    stores = dict(map(   lambda wid: (wid,builder.get_object(wid)),   store_ids   ))
    inputs_ids = ["number_to_generate_spinner"]
    inputs = dict(map(   lambda wid: (wid,builder.get_object(wid)),   inputs_ids   ))
    
    handler = GUIHandler(windows,stores,inputs)
    builder.connect_signals( handler )
    preloadNamelists( handler )
    windows["main_window"].show_all()
    
    Gtk.main()

if __name__ == '__main__':
    runGUI()
