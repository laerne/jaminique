from gi import require_version
require_version('Gtk','3.0')
from gi.repository import Gtk

class AutoComboBoxHandler:
    def __init__( self, combo_box, combo_store, cfg, cfg_path, cfg_type = str ):
        self.combo_box_ = combo_box
        self.combo_store_ = combo_store
        self.cfg_ = cfg
        self.path_ = cfg_path
        self.default_path_ = cfg_path + [ 'default' ]
        self.presets_path_ = cfg_path + [ 'presets' ]
        self.type_ = cfg_type
        
        self.populate_combo_box()



    def populate_combo_box( self ):
        #self.combo_box_.clear()

        #possible_values = sorted( [ name for name in self.cfg_.get( *self.path_, default={} ).keys()
        #        if name[0] != '*' and name != "default" ] )
        possible_values = sorted( [ name for name in self.cfg_.get( *self.presets_path_ ) ] )
        self.combo_store_.clear()
        
        for value in possible_values:
            iterator = self.combo_store_.append( (value,"") )
            
        #Select 'default' value
        self.on_cfg_value_changed()


    
    def on_combo_box_changed( self, combo_box ):
        active_iter = combo_box.get_active_iter()
        
        #Fail if nothing is selected
        if active_iter == None:
            dialog = Gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK,
                    "Nothing selected.");
            dialog.run()
            dialog.destroy()
            return True

        #Change the value in cfg
        str_value = combo_box.get_model().get_value( active_iter, 0 )
        value = self.type_( str_value )
        self.cfg_.set( value, *self.default_path_ )
        return True



    def on_cfg_value_changed( self ):
        value = self.cfg_.get( *self.default_path_ )
        str_value = str( value )
        
        i = self.combo_store_.get_iter_first()
        while i != None:
            if self.combo_store_.get_value( i, 0 ) == str_value:
                self.combo_box_.set_active_iter( i )
                return True
            i = self.combo_store_.iter_next( i )

        #if this code is reached, there is no matching correct str_value in the store
        dialog = Gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                "No item with value %s to select." % repr(value) )
        dialog.run()
        dialog.destroy()
        



    def change_value( self, new_value ):
        self.cfg_.set( new_value, *self.default_path_ )
        self.on_cfg_value_changed()




