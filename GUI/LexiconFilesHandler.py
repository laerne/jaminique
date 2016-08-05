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

import Loader as Loader
import os.path

class LexiconFilesHandler:
    def __init__( self, treeview, cfg, cfg_path ):
        self.store_ = treeview.get_model()
        self.treeview_ = treeview
        self.cfg_ = cfg
        self.path_ = cfg_path
        self.lexiconCache = {}
        
        self.populate_lexicon()
    
    def populate_lexicon( self ):
        for filepath in sorted( self.cfg_.get("lexicon","files",default=[]) ):
            self.load_lexicon( filepath )
            
        self.treeview_.get_selection().select_all()
        


    def load_lexicon( self, filepath ):
        cachedLexicon = Loader.loadLexicon( filepath ) #TODO have cached dicts match Selector's Loader

        name = os.path.splitext( os.path.basename( filepath ) )[0]
        wordcount = len( cachedLexicon )
        weightcount = sum( cachedLexicon.values() )

        store_iterator = self.store_.append( None, (filepath,wordcount,weightcount,name) )
        self.lexiconCache[ filepath ] = cachedLexicon

        filepaths_cfg = self.cfg_.get( *list( self.path_ + ['files'] ), default=[] )
        if filepath not in filepaths_cfg:
            filepaths_cfg.append( filepath )
        
        return store_iterator



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




