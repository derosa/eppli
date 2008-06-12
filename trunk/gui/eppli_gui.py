#!/usr/bin/python
#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

from eppli_controller import eppli_controller
from core.const import HZ
from core.const import MAX_RT_PRIO

from gui.stats import dialogo_grafica
from gui.eppli_graph import eppli_graph_stats

from core.eppli_exceptions import *

class eppli_gui():
    def __init__(self):
        self.ruta_tasks = None
        self.running = False
        self.boton_running = False
        self.SCHED_TIMER = 1.0/HZ
        self.timer_id = None
        self.selected_proc = None
        self.graph_type = "TSLICE"
        self.graph_description={"TSLICE": "Timeslice disponible",
                                "PRIO": "Prioridad dinámica",
                                "PERCENT": "Porcentaje completado",
                                "SWITCHES": "Cambios de contexto"}
        
        self.eventos = { "on_mainWindow_destroy": gtk.main_quit,
                        "on_boton_show_stats_toggled": self.show_stats,
                        "on_combo_procesos_changed": self.change_stat_graph,
                        "on_boton_nuevo_clicked": self.new_emulation,
                        "on_boton_nuevas_tasks_dir_clicked": self.new_tasks_dir,
                        "on_boton_nueva_task_clicked": self.add_single_task,
                        "on_boton_start_pause_clicked": self.run_pause_clicked,
                        "on_boton_acercade_clicked": self.show_about, 
                        "on_boton_steps_clicked": self.run_steps,
                        "on_entry_num_pasos_activate": self.run_steps,
                        "on_drawActive_expose_event": self.expose_event,
                        "on_drawExpired_expose_event": self.expose_event}
                
        self.appXML = gtk.glade.XML("gui/eppli-glade3.glade")
        
        self.appXML.signal_autoconnect(self.eventos)
        self.eppliWindow = self.appXML.get_widget("mainWindow")
        self.text_steps = self.appXML.get_widget("entry_num_pasos")
        self.boton_start_pause = self.appXML.get_widget("boton_start_pause")
        self.widgets = self.init_widgets()
        self.controller = eppli_controller(self)
        self.init_trees()
        self.clear_text()
        
    def run(self):
        """ Inicia el GUI y el bucle principal de gtk."""
        #self.update_all()
        self.eppliWindow.show()
        gtk.main()
        
    def new_emulation(self, widget):
        """ Inicia una nueva emulación a partir de un directorio con procesos
        a emular"""
        if not self.show_question("La emulación actual se perderá.\n¿Seguro que \
desea iniciar una nueva emulación?"):
            return
        print "Iniciando nueva emulación"
        
        if self.widgets["boton_graph"].get_active():
            print "Boton pulsado, fuera!"
            self.widgets["boton_graph"].set_active(False)

        if self.running:
            self.toggle_run_button(start_emu=False)
            self.controller.del_scheduler()
            self.expose_event(None, None)
            self.clear_text()
            self.running = False

    def new_tasks_dir(self, boton):
        ruta_tasks = self.select_tasks_dir()
        print "Directorio:", ruta_tasks
        if ruta_tasks:
            try:
                self.controller.new_task_dir(ruta_tasks)
            except NoTaskOrIdleDir, e:
                print "Error al lanzar el planificador"
                self.show_error("No se pudo inicializar el planificador con el \
contenido del directorio seleccionado:\n<b>%s</b>" % e.message )
                self.running = False
                return
            self.running = True    
            self.controller.done = False        
            self._update_all()

    def add_single_task(self, boton):
        task_name = self.select_single_task()
        print "Tarea:", task_name
        if task_name:
            try:
                self.controller.add_single_task(task_name)
            except NoTaskOrIdleDir, e:
                print "Error al lanzar el planificador"
                self.show_error("No se pudo inicializar el planificador con el \
proceso seleccionado:\n<b>%s</b>" % e.message )
                self.running = False
                return
            self.running = True
            self.controller.done = False
            self._update_all()

    def select_single_task(self):
        res = None
        file = gtk.FileChooserDialog("Selección de proceso",
                                     self.eppliWindow, 
                                     gtk.FILE_CHOOSER_ACTION_OPEN,
                                     buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        file.set_select_multiple(False)

        filtro =  gtk.FileFilter()
        filtro.add_pattern("*.tsk")
        filtro.set_name("Procesos de EPPLI")
        file.set_filter(filtro)

        respuesta = file.run()
        if respuesta == gtk.RESPONSE_OK:
            res = file.get_filename()
            print "Seleccionado el proceso", res
        elif respuesta == gtk.RESPONSE_CANCEL:
            print "Ninguna tarea seleccionada."
        file.destroy()
        return res
        
    def _update_all(self, include_trees = False):
        """ Actualiza todos los datos en pantalla cada vez que se completa 
        una iteración del planificador. Esta función es llamada por el 
        controlador."""
        #print "GUI - Actualizando datos de la vista"
        self.__update_stats_current()
        self.__update_stats_selected()
        self.__update_stats_scheduler()

        if self.controller.get_did_sched() or include_trees:
            self.__update_active_tree()
            self.__update_expired_tree()
        
        self.__update_bitmap_active()
        self.__update_bitmap_expired()
        if gtk.events_pending():
            gtk.main_iteration()

        
    def __update_stats_current(self):
        """ Actualiza las estadísticas del proceso current."""
        current = self.controller.get_current()
        self.__update_stats_text("current", current)

    def __update_stats_selected(self):
        """ Actualiza las estadísticas del proceso seleccionado."""
        # Buscar procname en los árboles...
        if self.selected_proc:
            selected = self.controller.get_task(self.selected_proc)
            self.__update_stats_text("selected", selected)
            self.clear_selections()
        return

    def __update_stats_text(self, prefix, procmap):
        """ Actualiza los textos de las estadísticas."""
        for k in procmap.keys():
            name ="text_%s_%s" % (prefix, k)
            cadena = str(procmap[k])
            try:
                self.widgets[name].set_label(cadena)
            except KeyError:
                print "Error al establecer %s a %s" % (name, cadena) 
                
    def __update_stats_scheduler(self):
        """ Actualiza las estadísticas del planificador."""
        procmap = self.controller.get_sched_stats()
        self.__update_stats_text("state", procmap)
        
        # Por hacer bonito, ponemos en negrita el valor del tiempo de ejecución
        # si coincide con llamada a scheduler.
        if self.controller.get_did_sched():
            marca = "<b>%s</b>" % self.widgets["text_state_runtime"].get_text()
            self.widgets["text_state_runtime"].set_label(marca)
            
    def __update_trees(self, nombre, data):
        """ Actualiza el contenido de los árboles"""
        tv = self.widgets["tree_view_%s" % nombre]
        treestore = self.widgets["tree_store_%s" % nombre]
        treestore.clear()
        keys = data.keys()
        keys.sort()
        for prio in keys:
             padre = treestore.append(None, ['Prioridad %d' % prio])
             for proc in data[prio]:
                 treestore.append(padre, ["%s" % proc])
                 
        tv.get_column(0).set_sort_order(gtk.SORT_ASCENDING)
        tv.set_model(treestore)
        tv.expand_all()
    
    def __update_active_tree(self):
        """ Actualiza el árbol de procesos activos"""
        active_data = self.controller.get_active_data()
        #print "Datos para el activeTree:", active_data
        self.__update_trees("active", active_data)
        
    def __update_expired_tree(self):
        expired_data = self.controller.get_expired_data()
        #print "Datos para el expiredTree:", expired_data
        self.__update_trees("expired", expired_data)
        
    def __update_bitmap_active(self):
        """ Actualiza la imagen del bitmap active y el número de procesos
        que tiene asignados."""
        bits = self.controller.get_bitmap_active()
        draw = self.widgets["bitmapActiveDraw"]
        self.__update_bitmap(draw, bits)
    
    def __update_bitmap_expired(self):
        """ Actualiza la imagen del bitmap expired y el número de procesos
        que tiene asignados."""
        bits = self.controller.get_bitmap_expired()
        draw = self.widgets["bitmapExpiredDraw"]
        self.__update_bitmap(draw, bits)
   
    def __update_bitmap(self, draw, bits):
        """ Actualiza la imagen de drawable con los valores pasados en bits"""
        win = draw.window
        gc = win.new_gc()
        win.clear()
        x1 = 0
        x2 = 280
        y = 25
        
        # Colores de 
        # http://sedition.com/perl/rgb.html
        col_prio_normal = win.get_colormap().alloc_color("CornflowerBlue")
        col_prio_rt = win.get_colormap().alloc_color("orange1")
        col_rect = win.get_colormap().alloc_color("gray")
        col_rect_fondo = win.get_colormap().alloc_color("gray100")
        
        gc.foreground = col_rect_fondo
        win.draw_rectangle(gc, True, x1, 0, x2, y+1)

        gc.foreground = col_rect
        win.draw_rectangle(gc, False, x1, 0, x2, y+1)
        
        for x in bits:
            if x <= MAX_RT_PRIO:
                gc.foreground = col_prio_rt
            else:
                gc.foreground = col_prio_normal
            win.draw_line(gc, x*2, 1, x*2, y)
            win.draw_line(gc, x*2+1, 1, x*2+1, y)
        
    
    def expose_event(self, area, evento):
        self.__update_bitmap_active()
        self.__update_bitmap_expired()

    def check_sched_init(self):
        if not self.running:
            self.show_error("""¡El emulador no tiene procesos! Añada alguno.""")

        return self.running
        
    def run_pause_clicked(self, boton):
        """ Ejecuta y pausa la ejecución del planificador.
        También alterna el aspecto del botón para reflejar la pausa."""
        
        if not self.check_sched_init():
            return
        if self.controller.stepping:
            self.show_error("""¡El emulador ya está en funcionamiento en modo de pasos!\n
Espere a que finalicen los pasos solicitados.""")
            return
        if self.boton_running:
            self.toggle_run_button(start_emu=False)
        else:
            if self.controller.done:
                self.show_info("La emulación ha terminado.")
                return
            self.toggle_run_button(start_emu=True)
            
    def run_steps(self, boton):
        if not self.check_sched_init():
            return
        
        #Ya hemos pulsado el botón o enter en la cajita de texto
        if self.controller.stepping:
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

        if self.controller.done:
            self.show_info("La emulación ha terminado.")

        self.controller.sched_step(steps, True)

    def select_tasks_dir(self):
        """ Abre un cuadro de diálogo para seleccionar el directorio que 
        contiene las tareas a emular."""
        res = None
        file = gtk.FileChooserDialog("Selección de carpeta de procesos",
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
        """ Inicia el temporizador que ejecuta periodicamente los pasos del 
        planificador"""
        self.timer_id = gobject.timeout_add(int(self.SCHED_TIMER * 1000), 
                                            self.controller.sched_step)
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
               "last_ran", "array", "class", "interactive"]
        for p in proc:
            for a in atr:
                name = "text_%s_%s" % (p, a)
                wobj = self.appXML.get_widget(name)
                res[name] = wobj
        
        # Objetos de las estadísticas del scheduler
        atr = ["runtime", "nr", "nr_switch", "best_prio", "num_active", "num_expired"]
        for a in atr:
            name = "text_state_%s" % a
            wobj = self.appXML.get_widget(name)
            res[name] = wobj
            
        # Los Drawable donde pintar los bitmaps...
        res["bitmapActiveDraw"] = self.appXML.get_widget("drawActive")
        res["bitmapExpiredDraw"] = self.appXML.get_widget("drawExpired")
        
        res["bitmapActiveDraw"].connect("expose-event", self.expose_event)
        res["bitmapExpiredDraw"].connect("expose-event", self.expose_event)
        
        res["tree_view_active"] = self.appXML.get_widget("tree_view_active")
        res["tree_view_expired"] = self.appXML.get_widget("tree_view_expired")
        res["tree_store_active"] = gtk.TreeStore(str)
        res["tree_store_expired"] = gtk.TreeStore(str)
        
        res["boton_start_pause"] = self.appXML.get_widget("boton_start_pause")
        
        res["boton_graph"] =self.appXML.get_widget("boton_show_stats")
        res["window_stats"] = self.appXML.get_widget("window_stats")
        res["combo_procesos"] = self.appXML.get_widget("combo_procesos")
        res["image_stats"] = self.appXML.get_widget("image_stats_graph")
        
        res["radio_prio"] = self.appXML.get_widget("radio_prio")
        res["radio_tslice"] = self.appXML.get_widget("radio_tslice")
        res["radio_percent"] = self.appXML.get_widget("radio_percent")
        res["radio_sched"] = self.appXML.get_widget("radio_scheduler")
        
        res["radio_prio"].connect("toggled", self.select_graph_type, "PRIO")
        res["radio_tslice"].connect("toggled", self.select_graph_type, "TSLICE")
        res["radio_percent"].connect("toggled", self.select_graph_type, "PERCENT")
        res["radio_sched"].connect("toggled", self.select_graph_type, "SWITCHES")
        
        
        return res
    
    def init_trees(self):
        """Inicializa la estructura de los árboles active y expired"""
        for name in ["active", "expired"]:
            tv = self.widgets["tree_view_%s" % name]
            model = self.widgets["tree_store_%s" % name]
            tvcolumn = gtk.TreeViewColumn("Procesos en '%s'" % name)
            tv.append_column(tvcolumn)
            cell = gtk.CellRendererText()
            tvcolumn.pack_start(cell, True)
            tvcolumn.add_attribute(cell, 'text', 0)
            tvcolumn.set_sort_column_id(0)
            tv.set_model(model)
            select = tv.get_selection()
            select.set_mode(gtk.SELECTION_SINGLE)
            select.connect("changed", self.get_selected_task)

    def get_selected_task(self, sel):
        """Establece el nombre del proceso seleccionado en un árbol"""
        (store, iter) = sel.get_selected()
        #print "Lo de la selección: %s, %s" % (store, iter)
        if iter and store.iter_depth(iter):
            self.selected_proc = store.get_value(iter, 0)
        else:
            self.selected_proc = None
        self.__update_stats_selected()

    def clear_text(self):
        """ Elimina el texto de las etiquetas"""
        ws = self.appXML.get_widget_prefix("text_")
        for w in ws:
            w.set_label("")
        for t in ["active", "expired"]:
            treestore = self.widgets["tree_store_%s" % t]
            treestore.clear()
    
    def clear_selections(self):
        """ Elimina las selecciones de los treeview para evitar tener una 
        selección en cada árbol"""
        for t in ["active", "expired"]:
            tv = self.widgets["tree_view_%s" % t]
            sel = tv.get_selection()
            sel.unselect_all()
            
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

    def show_info(self, msg):
        """ Muestra un mensaje de información"""
        d = gtk.MessageDialog(self.eppliWindow, 
                              gtk.DIALOG_MODAL, 
                              gtk.MESSAGE_INFO,
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
    
    def show_about(self, boton):
        win = gtk.AboutDialog()
        win.set_comments("Emulador del Planificador de Procesos de Linux\n2.6.11")
        win.set_name("EPPLI")
        win.set_version("0.1")
        win.set_copyright("David Erosa García, 2008")
        win.set_authors(["David Erosa García"])
        win.run()
        win.destroy()

    def toggle_run_button(self, start_emu):
        """ Alterna el estado del botón de ejecución/pausa
        True - Inicia la emulación.
        False - Detiene la emulación"""
        boton = self.widgets["boton_start_pause"]
        if start_emu:
            # Inicia el timer del emulador y pone el botón en modo "pausa"
            self.start_timer()
            boton.set_label("Pausar")
            boton.set_stock_id("gtk-media-pause")
        else:
            # Detiene el timer del emulador y pone el boton en modo "play"
            if self.timer_id:
                self.stop_timer()
            boton.set_label("Iniciar")
            boton.set_stock_id("gtk-media-play")
            print "GUI - Eliminando timer para sched_step"
            # Pausa la ejecución

    def show_stats(self, boton):
        """ Muestra el cuadro de la gráfica estadísticas"""        
        if not self.controller.has_sched():
            return
        win = self.widgets["window_stats"]
        if boton.get_active():
            combo = self.widgets["combo_procesos"]
            combo.get_model().clear()
            for t in self.controller.sched.stats["TSLICE"].tasks:
                combo.append_text(t)
            win.show()
        else:
            self.hide_stats()
            
    def hide_stats(self):
        """Oculta la ventana de gráficas estadísticas"""
        self.widgets["window_stats"].hide()
        
    def change_stat_graph(self, combo):
        """ Actualiza los datos de la gráfica"""
        if self.graph_type=="SWITCHES":
            self.render_stats()
            return
            
        activo = combo.get_active_text()
        if not activo: 
            return
        else:
            self.render_stats(activo)
            
    def render_stats(self, proceso= None):
        if not proceso:
            datos = self.controller.get_sched_stat_data()
        else:
            datos = self.controller.get_task_stat_data(self.graph_type, proceso)
        #print "Representando estadísticas: %s" % datos
        egs = eppli_graph_stats()
        egs.set_axis_title("Ticks", self.graph_description[self.graph_type])
        self.widgets["image_stats"].set_from_pixbuf((egs.generate_graph(datos)))

        
    def select_graph_type(self, radio, dato):
        
        print "Radio: %s: %s" % (dato, radio.get_active())
        if radio.get_active():
            self.graph_type = dato
            print "Seleccionado: %s" % self.graph_type
        self.change_stat_graph(self.widgets["combo_procesos"])    
        
if __name__ == "__main__":
    e = eppli_gui()
    e.run()