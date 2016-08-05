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



