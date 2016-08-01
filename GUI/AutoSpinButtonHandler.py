from gi import require_version
require_version('Gtk','3.0')
from gi.repository import Gtk

class AutoSpinButtonHandler:
    def __init__( self, spin_button, cfg, cfg_path, cfg_type = float ):
        self.spin_button_ = spin_button
        self.cfg_ = cfg
        self.path_ = cfg_path
        self.type_ = cfg_type

    def on_spin_button_changed( self ):
        value = None

        if self.type_ == int:
            value = self.spin_button_.get_value_as_int()
        else:
            value = self.type_( self.spin_button_.get_value() )

        self.cfg_.set( value, *self.path_ )


    def on_cfg_value_changed( self ):
        value = self.cfg_.get( *self.path_ )
        self.spin_button_( float(value) )


    def change_value( self, new_value ):
        self.cfg_.set( new_value, *self.path_ )
        self.on_cfg_value_changed()



