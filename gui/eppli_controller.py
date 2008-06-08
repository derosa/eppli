#coding: utf-8

import inspect
import gtk

from core.sched import scheduler
from core.bitutils import ffs
from core.bitutils import clear_bit
 

from core.eppli_exceptions import NotImplemented
from core.eppli_exceptions import NoTaskOrIdleDir

class eppli_controller():
    def __init__(self, parent):
        """ Inicia el controlador que controlará a 'parent' """
        
        print "Iniciando controlador de EPPLI"
        self.view = parent
        self.sched = None
        self.state_r = {0: "INTERRUPTIBLE", 1: "UNINTERRUPTIBLE", 
                        2: "RUNNING", 3: "EXIT"}
        self.policy_r = {0:"Tiempo Real - Round Robin", 1: "Tiempo Real - FIFO", 2: "Proceso normal"}
        
    def new_scheduler(self, ruta_tasks):
        """ Inicia un nuevo scheduler con las tareas de ruta_tasks."""
        self.del_scheduler()
        self.sched = scheduler(ruta_tasks)
    
    def del_scheduler(self):
        """ Elimina los datos del scheduler."""
        if self.sched:
            del self.sched
            self.sched = None
    
    def get_did_sched(self):
        return self.sched.did_sched
    
    def sched_step(self, steps=1):
        """ Avanza n pasos en el planificador y actualiza la vista."""
        self.stepping=True
        while steps:
            steps-=1
            # Avanza un tick en el emulador
            self.sched.do_ticks()
            # Pide a la vista que actualize los datos.
            self.view._update_all()
            if gtk.events_pending():
                gtk.main_iteration()

        self.stepping=False
        return True
    
    def get_current(self):
        """ Devuelve la tarea current del sistema."""
        return self.get_task(self.sched.current.name)
    
    def get_task(self, name):
        """ Devuelve la tarea de nombre name."""
        tareas = [t for t in self.sched.tasks if t.name == name]
        tarea = tareas[0]
        res = {}
        res["name"] = tarea.name
        res["state"] = self.state_r[tarea.state]
        res["prio"] = tarea.prio
        res["static_prio"] = tarea.static_prio
        res["sleep_avg"] = tarea.sleep_avg
        res["last_ran"] = tarea.last_ran
        res["array"] = tarea.array.name
        res["class"] = self.policy_r[tarea.policy]
        
        # Los procesos FIFO ignoran el timeslice y puede llegar a ser negativo.
        # Para evitar confusiones en el GUI, se muestra el siguiente mensaje
        if tarea.policy == 1:
            res["timeslice"] = "Proceso sin timeslice"
        else:
            res["timeslice"] = tarea.time_slice

        return res
    
    def get_sched_stats(self):
        """ Devuelve las estadísticas del planificador."""
        res ={}
        res["runtime"] = self.sched.cpu.clock
        res["nr"] = self.sched.cpu.rq.nr_running
        res["nr_switch"] = self.sched.cpu.rq.nr_switches
        res["best_prio"] = self.sched.cpu.rq.best_expired_prio
        res["num_active"] = "<i>%d procesos</i>" % self.sched.cpu.rq.active.nr_active
        res["num_expired"] = "<i>%d procesos</i>" % self.sched.cpu.rq.expired.nr_active
        
        return res
    
    def get_bitmap_active(self):
        """ Devuelve una lista de prioridades que representan los bits
        activados del bitmap del array active."""
        return self._get_bitmap("active")
        
    def get_bitmap_expired(self):
        """ Devuelve una lista de prioridades que representan los bits
        activados del bitmap del array expired."""
        return self._get_bitmap("expired")
    
    def _get_bitmap(self, name):
        """ Devuelve el bitmap del array solicitado."""
        res=[]
        if name == "expired":
            #print "GUI - Obteniendo bitmap de expired"
            bitmap = long(self.sched.cpu.rq.expired.bitmap)
        elif name == "active":
            #print "GUI - Obteniendo bitmap de active"
            bitmap = long(self.sched.cpu.rq.active.bitmap)
        #print "GUI - El bitmap:", bitmap
        
        while bitmap:
            t = ffs(bitmap)
            #print "GUI - Añadiendo %d al resultado" % t
            res.append(t)
            bitmap = clear_bit(bitmap, t)
        #print "GUI - Bits activos en %s: %s" % (name, res)
        return res
    
    def get_trees_data(self, name):
        """ Devuelve una lista de prioridades con sus procesos""" 
        res = {}
        if name == "active":
            data = self.sched.cpu.rq.active.queue
        elif name == "expired":
            data = self.sched.cpu.rq.expired.queue
        
        for k in data.keys():
            res[k]=[]
            for t in data[k]:
                res[k].append(t.name)
        return res
        
    def get_active_data(self):
        """ Devuelve la lista de prioridades de la cola activa"""
        return self.get_trees_data("active")
    
    def get_expired_data(self):
        """ Devuelve la lista de prioridades de la cola expired"""
        return self.get_trees_data("expired")