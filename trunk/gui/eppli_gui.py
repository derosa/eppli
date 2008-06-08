#!/usr/bin/python
#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
import inspect

from eppli_controller import eppli_controller
from core.const import HZ
from core.eppli_exceptions import *

class eppli_gui():
    def __init__(self):
        self.ruta_tasks = None
        self.running = False
        self.boton_running = False
        self.SCHED_TIMER = 1.0/HZ
        self.timer_id = None
        self.eventos = { "on_mainWindow_destroy": gtk.main_quit,
                        "on_boton_nuevo_clicked": self.new_emulation,
                        "on_boton_start_pause_clicked": self.run_pause_clicked,
                        "on_boton_steps_clicked": self.run_steps,
                        "on_text_num_pasos_activate": self.run_steps,
                        "on_text_num_pasos_focus": self.clear_text}
        
        self.appXML = gtk.glade.XML("gui/eppli.glade")
        self.appXML.signal_autoconnect(self.eventos)
        self.eppliWindow = self.appXML.get_widget("mainWindow")
        self.text_steps = self.appXML.get_widget("text_num_pasos")
        self.boton_start_pause = self.appXML.get_widget("boton_start_pause")
        self.widgets = self.init_widgets()
        self.controller = eppli_controller(self)

        
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
            self.stop_timer()

        self.ruta_tasks = self.select_tasks_dir()
        if self.ruta_tasks:
            self.controller.del_scheduler()
            try:
                self.controller.new_scheduler(self.ruta_tasks)
                self.running = True
                self.controller.sched_step()
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
        #self.__update_stats_selected()
        self.__update_stats_scheduler()
        #self.__update_trees()
        self.__update_bitmap_active()
        self.__update_bitmap_expired()
    
    def __update_stats_current(self):
        """ Actualiza las estadísticas del proceso current."""
        current = self.controller.get_current()
        self.__update_stats_text("current", current)

    def __update_stats_selected(self):
        """ Actualiza las estadísticas del proceso seleccionado."""
        raise NotImplemented(inspect.stack()[1][3])
#        # TODO: Hay que obtener el nombre del proceso seleccionado en el TreeView...
#        selected = self.controller.get_task(procname)
#        self.__update_stats_text("selected", selected)
        return
    
    def __update_stats_scheduler(self):
        """ Actualiza las estadísticas del planificador."""
        procmap = self.controller.get_sched_stats()
        self.__update_stats_text("state", procmap)

    def __update_stats_text(self, prefix, procmap):
        """ Actualiza los textos de las estadísticas."""
        for k in procmap.keys():
            name ="text_%s_%s" % (prefix, k)
            cadena = str(procmap[k])
            self.widgets[name].set_label(cadena) 

    def __update_trees(self):
        """ Actualiza el contenido de los árboles"""
        raise NotImplemented(inspect.stack()[0][3])
    
    def __update_bitmap_active(self):
        """ Actualiza la imagen del bitmap active y el número de procesos
        que tiene asignados."""
        bits = self.controller.get_bitmap_active()
        draw = self.widgets["treeActiveDraw"]
        self.__update_bitmap(draw, bits)
    
    def __update_bitmap_expired(self):
        """ Actualiza la imagen del bitmap expired y el número de procesos
        que tiene asignados."""
        bits = self.controller.get_bitmap_expired()
        draw = self.widgets["treeExpiredDraw"]
        self.__update_bitmap(draw, bits)
   
    def __update_bitmap(self, draw, bits):
        """ Actualiza la imagen de drawable con los valores pasados en bits"""
        win = draw.window
        gc = win.new_gc()
        win.clear()
        X1 = 0
        X2 = 280
        Y = 25
        celeste = win.get_colormap().alloc_color("light blue")
        rojo = win.get_colormap().alloc_color("red")
        gc.foreground = rojo
        win.draw_rectangle(gc, False, X1, 0, X2, Y+1)
        gc.foreground = rojo
        for x in bits:
           win.draw_line(gc, x*2, 0, x*2, Y)
           win.draw_line(gc, x*2+1, 0, x*2+1, Y)
        gtk.main_iteration()
        
    def check_sched_init(self):
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
        
        if not self.check_sched_init():
            return
        
        if self.boton_running:
            boton.set_label("Iniciar")
            boton.set_stock_id("gtk-media-play")
            print "GUI - Eliminando timer para sched_step"
            # Pausa la ejecución
            self.stop_timer()
        else:
            boton.set_label("Pausar")
            boton.set_stock_id("gtk-media-pause")
            self.start_timer()
            
    def run_steps(self, boton):
        if not self.check_sched_init():
            return
        
        if self.timer_id:
            self.show_error("""¡El emulador ya está en funcionamiento!\n
Pauselo si desea avanzar por pasos.""")
            return
            
        try:
            steps = int(self.text_steps.get_text())
        except ValueError:
            self.show_error("El valor de los pasos debe ser numérico")
            return
        self.boton_start_pause.unset_flags(gtk.SENSITIVE)
        self.controller.sched_step(steps)
        self.boton_start_pause.set_flags(gtk.SENSITIVE)
            
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
    
    def start_timer(self):
        t = int(self.SCHED_TIMER * 1000)
        print "GUI - Iniciando el timer para sched_step (%d)" % t
        self.timer_id = gobject.timeout_add(int(self.SCHED_TIMER * 1000), self.controller.sched_step)
        self.boton_running = True
    
    def stop_timer(self):
        gobject.source_remove(self.timer_id)
        self.timer_id = None
        self.boton_running = False        
    
    def init_widgets(self):
        """ Devuelve un map de la forma (nombre_widget:objecto)*"""
        res = {}

        # Objetos con los datos de current y selected
        proc = ["current", "selected"]
        atr = ["name", "state", "timeslice", "prio", "static_prio", "sleep_avg",
               "last_ran", "array", "class"]
        for p in proc:
            for a in atr:
                name = "text_%s_%s" % (p, a)
                wobj = self.appXML.get_widget(name)
                res[name] = wobj
        
        # Objetos de las estadísticas del scheduler
        atr = ["runtime", "nr", "nr_switch", "best_prio"]
        for a in atr:
            name = "text_state_%s" % a
            wobj = self.appXML.get_widget(name)
            res[name] = wobj
            
        # Los Drawable donde pintar los bitmaps...
        res["treeActiveDraw"] = self.appXML.get_widget("drawActive")
        res["treeExpiredDraw"] = self.appXML.get_widget("drawExpired") 
        
        return res
    
    def clear_text(self, texto, nada):
        self.text_steps.set_text("")
    
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
