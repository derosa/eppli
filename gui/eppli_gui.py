#!/usr/bin/python
#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

from eppli_controller import eppli_controller
from eppli_controller import NotImplemented

class eppli_gui():
    def __init__(self):
        self.eventos = { "on_mainWindow_destroy": gtk.main_quit,
                        "on_boton_nuevo_clicked": self.select_tasks_dir,
                        "on_boton_start_pause_toggled": self.run_pause}
        
        self.appXML = gtk.glade.XML("eppli.glade")
        self.appXML.signal_autoconnect(self.eventos)
        
        sel.eppliWindow = self.appXML.get_widget("mainWindow")
        
        self.controller = eppli_controller(self)
        
    def run(self):
        self.update_all()
        self.appXML.show()
    
    def update_all(self):
        raise NotImplemented()
        
if __name__ == "__main__":
    e = eppli_gui()
    e.run()
