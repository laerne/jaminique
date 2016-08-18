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

from .GtkUtilities import make_float_data_func
from utilities import int_to_human_readable_str

import Loader
import os.path
import os

class LexiconFilesHandler:
    def __init__( self, treeview, cfg, cfg_path, builder=None ):
        self.store_ = treeview.get_model()
        self.treeview_ = treeview
        self.cfg_ = cfg
        self.path_ = cfg_path
        
        #Set the byte function
        if builder:
            def size_data_func( colunmn, cell, model, iter, _ ):
                    size = model.get(iter,1)[0]
                    text = "%s" % int_to_human_readable_str( size )
                    cell.set_property("text", text)

            builder.get_object("column_size").set_cell_data_func(
                    builder.get_object("size_renderer"), size_data_func )
            builder.get_object("column_weight").set_cell_data_func(
                    builder.get_object("weight_renderer"), make_float_data_func("%.2f",2) )
        
        self.populate_lexicon()
    
    def populate_lexicon( self ):
        filepaths = Loader.findFilesFromPatterns( self.cfg_.get("lexicon","files",default=[]) )
        for filepath in sorted(filepaths):
            self.load_lexicon( filepath )
            
        self.treeview_.get_selection().select_all()
        


    def load_lexicon( self, filepath ):
        it = self.update_lexicon( filepath )
        if it == None:
            return self.append_lexicon( filepath )
        else:
            return it

    def append_lexicon( self, filepath ):
        name = os.path.splitext( os.path.basename( filepath ) )[0]
        size = os.stat( filepath ).st_size
        weight = 1.0
        store_iterator = self.store_.append( None, (filepath,size,weight,name) )

        filepaths_cfg = self.cfg_.get( *list( self.path_ + ['files'] ), default=[] )
        if filepath not in filepaths_cfg:
            filepaths_cfg.append( filepath )
        
        return store_iterator
    
    def update_lexicon( self, filepath ):
        it = self.store_.get_iter_first()
        while it != None:
            it_filepath = self.store_.get_value( it, 0 )
            
            if it_filepath == filepath:
                size = os.stat( filepath ).st_size
                self.store_.set_value( it, 1, size )
                return it
                
            it = self.store_.iter_next( it )

        return None



    def on_add_lexicon( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Open lexicon file",
                None,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                )
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selection = self.treeview_.get_selection()
            selection.unselect_all()
            for filename in dialog.get_filenames():
                new_iter = self.load_lexicon( filename )
                selection.select_iter( new_iter )
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

        return True



    def on_remove_lexicon( self, selection ):
        store, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: store.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            store.remove( row_iter )
        return True


    def yield_filepaths_from_selection( self, selection = None ):
        if not selection:
            selection = self.treeview_.get_selection()

        store, row_paths =  selection.get_selected_rows()
        for row_path in row_paths:
            yield store.get_value( store.get_iter( row_path ), 0 )




