#!/usr/bin/python
#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

from eppli_controller import eppli_controller
from core.eppli_exceptions import *

class eppli_gui():
    def __init__(self):
        self.eventos = { "on_mainWindow_destroy": gtk.main_quit,
                        "on_boton_nuevo_clicked": self.new_emulation,
                        "on_boton_start_pause_toggled": self.run_pause}
        
        self.appXML = gtk.glade.XML("gui/eppli.glade")
        self.appXML.signal_autoconnect(self.eventos)
        self.eppliWindow = self.appXML.get_widget("mainWindow")
        self.controller = eppli_controller(self)
        self.ruta_tasks = None
        self.running = False
        
    def run(self):
        """ Inicia el GUI y el bucle principal de gtk."""
        #self.update_all()
        self.eppliWindow.show()
        gtk.main()
        
    def new_emulation(self, widget):
        """ Inicia una nueva emulación a partir de un directorio con procesos
        a emular"""
        if self.running:
            if not self.show_question("La emulación actual se perderá, ¿Seguro que \
desea iniciar una nueva emulación?"):
                return
        
        self.ruta_tasks = self.select_tasks_dir()
        if self.ruta_tasks:
            self.controller.del_scheduler()
            try:
                self.controller.new_scheduler(self.ruta_tasks)
                self.running = True
            except NoTaskOrIdleDir, e:
                print "Error al lanzar el planificador"
                self.show_error("No se pudo inicializar el planificador con el \
contenido del directorio seleccionado:\n<b>%s</b>" % e.message )
                self.running = False
    
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
    
    def run_pause(self, boton):
        """ Ejecuta y pausa la ejecución del planificador.
        También alterna el aspecto del botón para reflejar la pausa."""
        if not boton.get_active():
            # El botón está no-pulsado
            boton.set_label("Iniciar")
        else:
            boton.set_label("Pausar")
            
        raise NotImplemented()
    
    def select_tasks_dir(self):
        """ Abre un cuadro de diálogo para seleccionar el directorio que 
        contiene las tareas a emular."""
        res = None
        file = gtk.FileChooserDialog("Selección de carpeta de tareas",
                                     self.eppliWindow, 
                                     gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                     buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        respuesta = file.run()
        if respuesta == gtk.RESPONSE_OK:
            res = file.get_filename()
            print "Seleccionado el directorio", res
        elif respuesta == gtk.RESPONSE_CANCEL:
            res = None
            print "Ningún directorio seleccionado."
        file.destroy()
        return res
    
    def show_error(self, msg):
        d = gtk.MessageDialog(self.eppliWindow, 
                              gtk.DIALOG_MODAL, 
                              gtk.MESSAGE_ERROR,
                              gtk.BUTTONS_OK,
                              None)
        d.set_markup(msg)
        res = d.run()
        d.destroy()

    def show_question(self, t):
        d = gtk.MessageDialog(self.eppliWindow, 
                              gtk.DIALOG_MODAL, 
                              gtk.MESSAGE_WARNING, 
                              gtk.BUTTONS_YES_NO, 
                              t)
        res = d.run()
        d.destroy()
        return ( res == gtk.RESPONSE_YES )
        
if __name__ == "__main__":
    e = eppli_gui()
    e.run()
