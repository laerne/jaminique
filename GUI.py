from gi.repository import Gtk
from gi.repository import Gdk
import os.path
from sys import argv

import PrefixCounter
import Generator

glade_prefix = os.path.join( os.path.dirname( argv[0] ), "glade" )

class GUIHandler(object):
    def __init__( self, windows, stores ):
        self.windows = windows
        self.stores = stores
        
    def on_main_window_destroy( self, window ):
        Gtk.main_quit()
        return True
    
    def on_add_dictionary( self, dialog ):
        dialog.show()
        return True
    
    def on_remove_dictionary( self, selection ):
        dictionaries, row_paths =  selection.get_selected_rows()
        row_iters = list(map( lambda path: dictionaries.get_iter( path ), row_paths ))
        for row_iter in row_iters:
            dictionaries.remove( row_iter )

    def on_delete_dictfile_chooser_dialog( self, dialog, eventType ):
        dialog.hide()
        #self.windows["dictfile_chooser"].hide()
        return True
    
    def on_dictfile_chooser_close_button_clicked( self, dialog ):
        dialog.hide()
        #self.windows["dictfile_chooser"].hide()
        return True
    
    def on_dictfile_chooser_add_button_clicked( self, dialog ):
        dictionaries = self.stores["dictionaries"]

        for uri in dialog.get_uris():
            assert uri[:7] == "file://"
            filepath = uri[7:]
            name = os.path.splitext( os.path.basename( filepath ) )[0]
            dictionaries.append( None, (filepath,1,1.0,name,True) )
            
        dialog.hide()
        return True
    
    def on_is_used_selector_toggled( self, toggleButton, row_path ):
        dictionaries = self.stores["dictionaries"]
        row_iter = dictionaries.get_iter( row_path )
        #print( "You clicked %s" % repr(dictionaries.get_value( row_iter, 0 )) )
        former_value = dictionaries.get_value( row_iter, 4 )
        dictionaries.set( row_iter, [4], [not former_value] )
        pass
    

def runGUI():
    glade_path = os.path.join( glade_prefix, "main_ui.glade" )
    builder = Gtk.Builder.new_from_file( glade_path )
    
    window_ids = ["main_window","dictfile_chooser"]
    windows = dict(map(   lambda wid: (wid,builder.get_object(wid)),   window_ids   ))
    store_ids = ["dictionaries","generated_names"]
    stores = dict(map(   lambda wid: (wid,builder.get_object(wid)),   store_ids   ))
    
    builder.connect_signals( GUIHandler(windows,stores) )
    windows["main_window"].show_all()
    
    Gtk.main()

if __name__ == '__main__':
    runGUI()
