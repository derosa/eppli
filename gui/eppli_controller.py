#coding: utf-8

import inspect
import gtk

from time import sleep
import os

from core.sched import scheduler
from core.bitutils import ffs
from core.bitutils import clear_bit

from core.const import HZ
 
from core.eppli_exceptions import NotImplemented
from core.eppli_exceptions import NoTaskOrIdleDir

class eppli_controller():
    def __init__(self, parent):
        """ Inicia el controlador que controlará a 'parent' """
        
        print "Iniciando controlador de EPPLI"
        self.view = parent
        self.sched = None
        self.stepping = False
        self.state_r = {0: "INTERRUPTIBLE", 1: "UNINTERRUPTIBLE", 
                        2: "RUNNING", 3: "EXIT"}
        self.policy_r = {0:"Tiempo Real - Round Robin", 1: "Tiempo Real - FIFO", 2: "Proceso normal"}
        
    def new_scheduler(self, ruta_tasks):
        """ Inicia un nuevo scheduler con las tareas de ruta_tasks."""
        self.del_scheduler()
        self.sched = scheduler(ruta_tasks)
        self.done = False
    
    def del_scheduler(self):
        """ Elimina los datos del scheduler."""
        if self.sched:
            del self.sched
            self.sched = None
            self.stepping = False
            self.done = True
     
    def has_sched(self):
        return (self.sched != None)

    def new_task_dir(self, ruta):
        for dir, subdir, files in os.walk(ruta):
                if dir == ruta:                    
                    tareas = [os.path.join(ruta, d) for d in files if d.endswith(".tsk")]
                    print "new_task_dir: tareas actuales:", tareas
        
        if not tareas:
            error = "'%s' no contiene ficheros con procesos." % ruta
            raise NoTaskOrIdleDir(error)
        
        if not self.sched:
            self.new_scheduler(tareas)
        else:
            self.sched.add_tasks(tareas)
        self.view._update_all(True)
    
    def add_single_task(self, task_name):
        # No se pueden añadir tareas sin un scheduler creado.
        if not self.sched:
            t = [task_name]
            print "Añadiendo proceso: ", t
            self.new_scheduler(t)
        else:
            self.sched.add_single_task(task_name)
        self.view._update_all(True)

    def get_did_sched(self):
        return self.sched.did_sched
    
    def sched_step(self, steps=1, stepping=False):
        """ Avanza n pasos en el planificador y actualiza la vista."""
        if self.done:
            return
        # Indica que estamos ejecutándonos por el método de pasos
        self.stepping=stepping

        while steps:
            steps-=1
            # Avanza un tick en el emulador
            procs = self.sched.do_ticks()
            # Pide a la vista que actualize los datos.
            self.view._update_all()
            if not procs:
                # Ya no nos estamos ejecutando por pasos
                self.stepping=False
                # Emulación finalizada
                self.done=True
                # Pongo el boton de inicio/pausa en el estado inicial
                self.view.toggle_run_button(start_emu=False)
                # Devuelvo False por si nos ejecutamos con el temporizados, 
                # para cancelarlo.
                self.view.show_info("La emulación ha finalizado.")
                return False
            sleep(0.1/HZ)
        self.stepping=False
        return True
    
    def get_current(self):
        """ Devuelve la tarea current del sistema."""
        return self.get_task(self.sched.current.name)
    
    def get_task(self, name):
        """ Devuelve la tarea de nombre name."""
        tareas = [t for t in self.sched.tasks if t.name == name]
        if not tareas:
            tareas = [self.sched.cpu.idle_task]
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
        res["interactive"] = (tarea.interactive() and "<b>Interactiva</b>") or ("No interactiva")
        #print "Datos de la tarea:\n%s" % res
        
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
        res = []
        if not self.has_sched():
            return res
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
    
    def get_tree_data(self, name):
        """ Devuelve una lista de prioridades con sus procesos""" 
        res = {}
        if name == "active":
            data = self.sched.cpu.rq.active.queue
        elif name == "expired":
            data = self.sched.cpu.rq.expired.queue
        
        #print "GUI - get_tree_data: %s" % data
        for k in data.keys():
            res[k]=[]
            for t in data[k]:
                res[k].append(t.name)

        return res
    
    def get_active_data(self):
        """ Devuelve la lista de prioridades de la cola activa"""
        return self.get_tree_data("active")
    
    def get_expired_data(self):
        """ Devuelve la lista de prioridades de la cola expired"""
        return self.get_tree_data("expired")
    
    def get_task_stat_data(self, type, name):
        # De momento muestro la de current, luego ya se verá...
        try:
            #print "Devolviendo datos de %s sobre %s" % (name, type)
            ret = self.sched.stats[type].get_task_data(name)
        except KeyError:
            ret = None
        return ret
    
    def get_sched_stat_data(self):
        return self.sched.stats["SWITCHES"].get_sched_data()
        
