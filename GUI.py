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


from ArgumentTree import ArgumentTree
import SmoothMarkov
import Loader
import Writer
import Selector
from utilities import warn, fail

from gi import require_version
require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import os.path
from sys import argv

glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )


#The GUI data rule: Data in arguments (of type ArgumentTree) cannot be changed
#   EXCEPT WHEN the data is a duplicate/inializer of a GUI value, that is updated when the GUI is.

class GUIHandler(object):
    def __init__( self, builder, arguments ):
        self.builder = builder
        self.arguments = arguments
        self.dictionaries = {}
        
    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True
        
    def load_lexicon( self, filepath ):
        lexicon_data = self.builder.get_object("dictionaries")
        cachedLexicon = Loader.loadLexicon( filepath ) #TODO have cached dicts match Selector's Loader
        
        name = os.path.splitext( os.path.basename( filepath ) )[0]
        wordcount = len( cachedLexicon )
        weightcount = sum( cachedLexicon.values() )
        
        lexicon_data.append( None, (filepath,wordcount,weightcount,name) )
        self.dictionaries[ filepath ] = cachedLexicon

        arguments_files = self.arguments.get( 'lexicon', 'files' )
        if filepath not in arguments_files:
            arguments_files .append( filepath )

    #TODO create a class that do this behavior both for tokenizer and generator
    def add_generation_method( self, name ):
        generation_algorithms_data = self.builder.get_object("generation_algorithms")
        iterator = generation_algorithms_data.append( (name,"") )
        #self.builder.get_object("generation_algo_selector").set_active_iter( iterator )
    
    def select_generation_method_by_name( self, name = None ):
        if name == None:
            name = self.arguments.get( 'generator', 'default' )
            
        generation_algorithms_data = self.builder.get_object("generation_algorithms")
        i = generation_algorithms_data.get_iter_first()
        while i != None:
            if generation_algorithms_data.get_value( i, 0 ) == name:
                self.builder.get_object("generation_algo_selector").set_active_iter( i )
                return
            i = generation_algorithms_data.iter_next( i )

        #if this code is reached, there is no algo of the correct name in the store
        dialog = Gtk.MessageDialog(
                self.builder.get_object("main_window"),
                0,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                "No generation algorithm with name %s to select." % repr(name) );
        dialog.run()
        dialog.destroy()
        
        
            
        
    def on_add_lexicon( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Open lexicon file",
                self.builder.get_object("main_window"),
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                )
        dialog.set_select_multiple(True)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():
                self.load_lexicon( filename )
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True
    
    def on_select_generation_algo( self, combo ):
        active_iter = combo.get_active_iter()
        if active_iter == None:
            dialog = Gtk.MessageDialog(
                    self.builder.get_object("main_window"),
                    0,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK,
                    "No generation algorithm selected.");
            dialog.run()
            dialog.destroy()
            return True
        else:
            name = combo.get_model().get_value( active_iter, 0 )
            self.arguments.set( name, 'generator', 'default' )
        return True
    
    def on_remove_lexicon( self, selection ):
        lexicon_data, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: lexicon_data.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            lexicon_data.remove( row_iter )
        return True
        
    def on_edit_lexicon( self, selection ):
        lexicon_data, row_paths =  selection.get_selected_rows()
        names_store = self.builder.get_object("generated_names")
        names_store.clear()

        for path in row_paths:
            filepath = lexicon_data.get_value( lexicon_data.get_iter( path ), 0 )
            for word, weight in self.dictionaries[ filepath ].items():
                names_store.append((word,weight))
            
        #names_store.append(("",0.0))
    
    def on_number_to_generate_value_changed( self, spin_button ):
        number_of_generations = spin_button.get_value_as_int()
        self.arguments.set( number_of_generations, 'number' )

    def on_generate_button_clicked( self, selection ):
        lexicon_data, selected_paths = selection.get_selected_rows()
        selected_files = []
        for path in selected_paths:
            iterator = lexicon_data.get_iter( path )
            value = lexicon_data.get_value( iterator, 0 )
            selected_files.append( value )
        self.arguments.set( selected_files, 'lexicon', '*selected_files' )
            
        for perplexity, name in Selector.generate( self.arguments ):
            self.builder.get_object("generated_names").append((name,perplexity))
        
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
            Writer.writeLexiconFromIterator( filename, store_iterator() )
            self.load_lexicon( filename )
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True
    
def buildGUI( arguments = None ):
    if arguments == None:
        arguments = ArgumentTree()
        
    glade_path = os.path.join( glade_prefix, "main_ui.glade" )
    builder = Gtk.Builder.new_from_file( glade_path )
    handler = GUIHandler( builder, arguments )
    
    builder.connect_signals( handler )
    builder.get_object("main_window").show_all()
    
    return handler, builder

def process( arguments ):
    handler, builder = buildGUI( arguments )
    
    #Add default dictionaries
    for filepath in sorted( arguments.get("lexicon","files",default=[]) ):
        handler.load_lexicon( filepath )
    #Add default generation methods
    generation_methods = sorted( [ name for name in arguments.get( "generator", default={} ).keys()
            if name[0] != '*' and name != "default" ] )
        
    for generation_method in generation_methods:
        handler.add_generation_method( generation_method )
    handler.select_generation_method_by_name()

    selection = builder.get_object("dictionaries_view-selection")
    selection.select_all()
    
    numberToGenerate = arguments.get('number',default=0)
    builder.get_object("number_to_generate_spinner").set_value( numberToGenerate )
    if arguments.get('gui','*autogenerate_at_start'):
        handler.on_generate_button_clicked( selection )
    
    Gtk.main()
