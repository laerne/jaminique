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

class LexiconHandler:
    def __init__( self, treeview ):
        self.store_ = treeview.get_model()
        self.treeview_ = treeview
        pass

    def on_entry_perplexity_edited( self, cell, iterstring, value  ):
        names_store = self.store_
        iter = names_store.get_iter( iterstring )
        names_store.set_value( iter, 1, value )

    def on_entry_name_edited( self, cell, iterstring, value  ):
        names_store = self.store_
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
        self.store_.clear()
        return True

    def on_save_entries( self, selection ):
        dialog = Gtk.FileChooserDialog(
                "Save generated names",
                None,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT),
                )

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            def store_iterator():
                for row in self.store_:
                    yield( row[0], row[1] )
            Writer.writeLexiconFromIterator( filename, store_iterator() )
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return None
        dialog.destroy()

        return filename

