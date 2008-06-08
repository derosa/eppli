#!/usr/bin/python
#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

from eppli_controller import eppli_controller
from core.const import HZ
from core.eppli_exceptions import *

class eppli_gui():
    def __init__(self):
        self.eventos = { "on_mainWindow_destroy": gtk.main_quit,
                        "on_boton_nuevo_clicked": self.new_emulation,
                        "on_boton_start_pause_clicked": self.run_pause_clicked}
        
        self.appXML = gtk.glade.XML("gui/eppli.glade")
        self.appXML.signal_autoconnect(self.eventos)
        self.eppliWindow = self.appXML.get_widget("mainWindow")
        self.controller = eppli_controller(self)
        self.ruta_tasks = None
        self.running = False
        self.boton_running = False
        self.SCHED_TIMER = 1.0/HZ
        
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
        print "GUI - Actualizando datos de la vista"
        self.__update_stats_current()
        self.__update_stats_selected()
        self.__update_stats_scheduler()
        self.__update_bitmap_active()
        self.__update_bitmap_expired()
    
    def __update_stats_current(self):
        """ Actualiza las estadísticas del proceso current."""
        current = self.controller.get_current()
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
    
    def run_pause_check(self):
        print "GUI - Comprobando run_pause_check"
        if not self.running:
            self.show_error("""No se ha inicializado correctamente el emulador.\n
Por favor, seleccione un directorio con tareas.""")
            return False
        else:
            return True
    
    def run_pause_clicked(self, boton):
        """ Ejecuta y pausa la ejecución del planificador.
        También alterna el aspecto del botón para reflejar la pausa."""
        
        if not self.run_pause_check():
            return
        
        if self.boton_running:
            boton.set_label("Iniciar")
            boton.set_stock_id("gtk-media-play")
            print "GUI - Eliminando timer para sched_step"
            # Pausa la ejecución
            gobject.source_remove(self.timer)
            self.timer_id = None
            self.boton_running = False
        else:
            boton.set_label("Pausar")
            boton.set_stock_id("gtk-media-pause")
            t = int(self.SCHED_TIMER*1000)
            print "GUI - Iniciando el timer para sched_step (%d)" % t
            self.timer = gobject.timeout_add(int(self.SCHED_TIMER*1000), 
                                             self.controller.sched_step)
            self.boton_running = True
            
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
        """ Muestra un mensaje de error"""
        d = gtk.MessageDialog(self.eppliWindow, 
                              gtk.DIALOG_MODAL, 
                              gtk.MESSAGE_ERROR,
                              gtk.BUTTONS_OK,
                              None)
        d.set_markup(msg)
        res = d.run()
        d.destroy()

    def show_question(self, t):
        """Realiza una pregunta al usuario. Devuelve True si responde SI, False
        si se responde NO"""
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
