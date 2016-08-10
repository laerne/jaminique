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
import Loader as Loader
import Writer as Writer
import Selector as Selector
from utilities import warn, fail

from gi import require_version
require_version('Gtk','3.0')
from gi.repository import Gtk
import os.path
from sys import argv #TODO use a ressource path

from .AutoComboBoxHandler import AutoComboBoxHandler
from .AutoSpinButtonHandler import AutoSpinButtonHandler
from .LexiconFilesHandler import LexiconFilesHandler
from .LexiconHandler import LexiconHandler

#TODO delete this awful stuff
glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )


#The GUI data rule: Data in arguments (of type ArgumentTree) cannot be changed
#   EXCEPT WHEN the data is a duplicate/inializer of a GUI value, that is updated when the GUI is.

class GUIHandler(object):
    def __init__( self, builder, arguments ):
        self.builder = builder
        self.arguments = arguments

        self.tokenizer_combo_box_manager = AutoComboBoxHandler(
                combo_box = self.builder.get_object("tokenizer_algo_selector"),
                combo_store = self.builder.get_object("tokenizer_algorithms"),
                cfg = arguments,
                cfg_path = ['tokenizer'],
                )

        self.generator_combo_box_manager = AutoComboBoxHandler(
                combo_box = self.builder.get_object("generation_algo_selector"),
                combo_store = self.builder.get_object("generation_algorithms"),
                cfg = arguments,
                cfg_path = ['generator'],
                )

        self.filters_combo_box_manager = AutoComboBoxHandler(
                combo_box = self.builder.get_object("filters_algo_selector"),
                combo_store = self.builder.get_object("filters_presets"),
                cfg = arguments,
                cfg_path = ['filters'],
                )

        self.number_to_generate_spinner_manager = AutoSpinButtonHandler(
                spin_button = self.builder.get_object("number_to_generate_spinner"),
                cfg = arguments,
                cfg_path = ['number'],
                cfg_type = int,
                )
                
        self.lexicon_files_manager = LexiconFilesHandler(
                treeview = self.builder.get_object("lexicon_view"),
                cfg = arguments,
                cfg_path = ['lexicon'],
                )
        
        self.lexicon_manager = LexiconHandler(
                treeview = self.builder.get_object("generated_names_view")
                )





    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True


    ### TOKENIZING METHOD SELECTION MANAGEMENT ###
    
    def on_tokenizer_algo_selector_changed( self, combo ):
        return self.tokenizer_combo_box_manager.on_combo_box_changed( combo )


    ### GENERATION METHOD SELECTION MANAGEMENT ###

    def on_generation_algo_selector_changed( self, combo ):
        return self.generator_combo_box_manager.on_combo_box_changed( combo )


    ### FILTERS METHOD SELECTION MANAGEMENT ###
    
    def on_filters_algo_selector_changed( self, combo ):
        return self.filters_combo_box_manager.on_combo_box_changed( combo )


    ### NUMBER TO GENERATE FIELD MANAGEMENT ###

    def on_number_to_generate_value_changed( self, spin_button ):
        return self.number_to_generate_spinner_manager.on_spin_button_changed()




    ### LEXICON MANAGER ###

    def on_add_lexicon( self, selection ):
        return self.lexicon_files_manager.on_add_lexicon( selection )


    def on_remove_lexicon( self, selection ):
        return self.lexicon_files_manager.on_remove_lexicon( selection )


    def on_edit_lexicon( self, selection ):
        return self.lexicon_files_manager.on_edit_lexicon( selection )


    def on_edit_lexicon( self, selection ):
        lexicon_data, row_paths =  selection.get_selected_rows()
        names_store = self.builder.get_object("generated_names")
        names_store.clear()

        #TODO use a loader from file first
        for path in row_paths:
            filepath = lexicon_data.get_value( lexicon_data.get_iter( path ), 0 )
            for word, weight in self.lexicon_files_manager.lexiconCache[ filepath ].items():
                names_store.append((word,weight))



    ### GENERATION BUTTON MANAGEMENT ###

    def on_generate_button_clicked( self, selection ):
        #TODO use cached small lexicons for name generation too.
        selected_files = list( self.lexicon_files_manager.yield_filepaths_from_selection() )
        self.arguments.set( selected_files, 'lexicon', '*selected_files' )

        try:
            for perplexity, name in Selector.generate( self.arguments ):
                self.builder.get_object("generated_names").append((name,perplexity))
        except Exception as e:
            import traceback
            traceback.print_exc()

            dialog = Gtk.MessageDialog(
                    self.builder.get_object("main_window"),
                    0,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK,
                    "Generation raised exception of type \"%s\":\n\n\"%s\"" % (type(e).__name__,str(e)) )
            dialog.run()
            dialog.destroy()
            

        return True



    ### LEXICON DISPLAYER MANAGEMENT ###

    def on_entry_perplexity_edited( self, cell, iterstring, value  ):
        return self.lexicon_manager.on_save_entries( selection )

    def on_entry_name_edited( self, cell, iterstring, value  ):
        return self.lexicon_manager.on_save_entries( selection )

    def on_add_entry( self, selection ):
        return self.lexicon_manager.on_add_entry( selection )

    def on_remove_entry( self, selection ):
        return self.lexicon_manager.on_remove_entry( selection )

    def on_remove_all_entries( self, selection ):
        return self.lexicon_manager.on_remove_all_entries( selection )

    def on_save_entries( self, selection ):
        filename = self.lexicon_manager.on_save_entries( selection )
        if filename:
            self.lexicon_files_manager.load_lexicon( filename )
            return True
        else:
            return False

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

    if arguments.get('gui','*autogenerate_at_start'):
        selection = builder.get_object("lexicon_view-selection")
        handler.on_generate_button_clicked( selection )

    Gtk.main()
