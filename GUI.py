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

import SmoothMarkov
import Loader
import Writer
import Selector
from utilities import warn, fail

glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )


#The GUI data rule: Data in arguments (of type Selector.Arguments) cannot be changed
#   EXCEPT WHEN the data is a duplicate/inializer of a GUI value, that is updated when the GUI is.

class GUIHandler(object):
    def __init__( self, builder, arguments ):
        self.builder = builder
        self.arguments = arguments
        self.dictionaries = {}
        
    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True
        
    def load_dictionary( self, filepath ):
        dictionary_data = self.builder.get_object("dictionaries")
        cachedDictionary = Loader.loadDictionary( filepath ) #TODO have cached dicts match Selector's Loader
        
        name = os.path.splitext( os.path.basename( filepath ) )[0]
        wordcount = len( cachedDictionary )
        weightcount = sum( cachedDictionary.values() )
        
        dictionary_data.append( None, (filepath,wordcount,weightcount,name) )
        self.dictionaries[ filepath ] = cachedDictionary

        arguments_files = self.arguments.get( 'dictionary', 'files' )
        if filepath not in arguments_files:
            arguments_files .append( filepath )
            
        
    def on_add_dictionary( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Open dictionary file",
                self.builder.get_object("main_window"),
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
        
    def on_edit_dictionary( self, selection ):
        dictionary_data, row_paths =  selection.get_selected_rows()
        names_store = self.builder.get_object("generated_names")
        names_store.clear()

        for path in row_paths:
            filepath = dictionary_data.get_value( dictionary_data.get_iter( path ), 0 )
            for word, weight in self.dictionaries[ filepath ].items():
                names_store.append((word,weight))
            
        #names_store.append(("",0.0))

    def on_generate_button_clicked( self, selection ):
        dictionary_data, selected_paths = selection.get_selected_rows()
        selected_files = []
        for path in selected_paths:
            iterator = dictionary_data.get_iter( path )
            value = dictionary_data.get_value( iterator, 0 )
            selected_files.append( value )
        self.arguments.set( selected_files, 'dictionary', '*selected' )
            
        numberOfGenerations = self.builder.get_object("number_to_generate_spinner").get_value_as_int()
        dictionary, tokenizer, generator, filters = Selector.selectDictionaryTokenizerGeneratorFilters( self.arguments )
        
        for n in range(numberOfGenerations):
            perpexity, name = generator.generateName()
            self.builder.get_object("generated_names").append((name,perpexity))
        
        return True

    def on_entry_perplexity_edited( self, cell, iterstring, value  ):
        names_store = self.builder.get_object("generated_names")
        iter = names_store.get_iter( iterstring )
        names_store.set_value( iter, 1, value )
        
    def on_entry_name_edited( self, cell, iterstring, value  ):
        names_store = self.builder.get_object("generated_names")
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
        self.builder.get_object("generated_names").clear()
        return True
        
    def on_save_entries( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Save generated names",
                self.builder.get_object("main_window"),
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT),
                )
                
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            def store_iterator():
                names_store = self.builder.get_object("generated_names")
                for row in names_store:
                    yield( row[0], row[1] )
            Writer.writeDictionaryFromIterator( filename, store_iterator() )
            self.load_dictionary( filename )
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True
    
def buildGUI( arguments = None ):
    if arguments == None:
        arguments = Selector.Arguments()
        
    glade_path = os.path.join( glade_prefix, "main_ui.glade" )
    builder = Gtk.Builder.new_from_file( glade_path )
    handler = GUIHandler( builder, arguments )
    
    builder.connect_signals( handler )
    builder.get_object("main_window").show_all()
    
    return handler, builder

def process( arguments ):
    handler, builder = buildGUI( arguments )
    
    for filepath in sorted( arguments.get("dictionary","files",default=[]) ):
        handler.load_dictionary( filepath )

    selection = builder.get_object("dictionaries_view-selection")
    selection.select_all()
    
    numberToGenerate = arguments.get('number',default=0)
    if numberToGenerate == 0:
        builder.get_object("number_to_generate_spinner").set_value( 1 )
        arguments.set(1,'number')
    else:
        builder.get_object("number_to_generate_spinner").set_value( numberToGenerate )
        handler.on_generate_button_clicked( selection )
    
    ##TODO set the counter box to the correct value based on the argument
    ##TODO Bind the value of those boxes with the values in the "arguments" store
    
    
        
    Gtk.main()
