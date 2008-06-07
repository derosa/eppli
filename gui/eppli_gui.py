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
        
        self.appXML = gtk.glade.XML("gui/eppli.glade")
        self.appXML.signal_autoconnect(self.eventos)
        
        self.eppliWindow = self.appXML.get_widget("mainWindow")
        
        self.controller = eppli_controller(self)
        
    def run(self):
        """ Inicia el GUI y el bucle principal de gtk."""
        #self.update_all()
        self.eppliWindow.show()
        gtk.main()
    
    def _update_all(self):
        """ Actualiza todos los datos en pantalla cada vez que se completa 
        una iteración del planificador. Esta función es llamada por el 
        controlador."""
        raise NotImplemented()
    
    def __update_stats_current(self):
        """ Actualiza las estadísticas del proceso current."""
        raise NotImplemented()

    def __update_stats_selected(self):
        """ Actualiza las estadísticas del proceso seleccionado."""
        raise NotImplemented()
    
    def __update_stats_scheduler(self):
        """ Actualiza las estadísticas del planificador."""
        raise NotImplemented()

    def __update_bitmap_active(self):
        """ Actualiza la imagen del bitmap active y el número de procesos
        que tiene asignados."""
        raise NotImplemented()
    
    def __update_bitmap_expired(self):
        """ Actualiza la imagen del bitmap expired y el número de procesos
        que tiene asignados."""
        raise NotImplemented()
   
    def __update_bitmap(self, drawable, bits):
       """ Actualiza la imagen de drawable con los valores pasados en bits"""
       raise NotImplemented()
    
    def run_pause(self, widget):
        """ Ejecuta y pausa la ejecución del planificador.
        También alterna el aspecto del botón para reflejar la pausa."""
        raise NotImplemented()
    
    def select_tasks_dir(self, widget):
        """ Abre un cuadro de diálogo para seleccionar el directorio que 
        contiene las tareas a emular."""
        raise NotImplemented() 
        
if __name__ == "__main__":
    e = eppli_gui()
    e.run()
