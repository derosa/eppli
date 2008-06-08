#/usr/bin/python
#coding: utf-8

from core.sched import scheduler
from core.sched import NoTaskOrIdleDir

from core.eppli_exceptions import NotImplemented


class eppli_controller():
    def __init__(self, parent):
        """ Inicia el controlador que controlará a 'parent' """
        
        print "Iniciando controlador de EPPLI"
        self.view = parent
        self.sched = None
        
    def new_scheduler(self, ruta_tasks):
        """ Inicia un nuevo scheduler con las tareas de ruta_tasks."""
        self.sched = scheduler(ruta_tasks)
    
    def del_scheduler(self):
        """ Elimina los datos del scheduler."""
        if self.sched:
            del self.sched
            self.sched = None
    
    def sched_step(self, steps=1):
        """ Avanza n pasos en el planificador y actualiza la vista."""
        while steps:
            steps-=1
            # Avanza un tick en el emulador
            self.sched.do_ticks()
            # Pide a la vista que actualize los datos.
            self.view._update_all()
    
    def get_current(self):
        """ Devuelve la tarea current del sistema."""
        return self.get_tasks(self.sched.current.name)
    
    def get_tasks(self, name):
        """ Devuelve la tarea de nombre name."""
        res = {}
        res["name"] = current.name
        res["estado"] = current.state
        res["timeslice"] = current.time_slice
        res["prio"] = current.prio
        res["static_prio"] = current.static_prio

        raise NotImplemented()
    
    def get_sched_stats(self):
        """ Devuelve las estadísticas del planificador."""
        raise NotImplemented()
    
    def _get_bitmap(self, name):
        """ Devuelve el bitmap del array solicitado."""
        raise NotImplemented()
    
    def get_bitmap_active(self):
        """ Devuelve una lista de prioridades que representan los bits
        activados del bitmap del array active."""
        raise NotImplemented()
    
    def get_bitmap_expired(self):
        """ Devuelve una lista de prioridades que representan los bits
        activados del bitmap del array expired."""
        raise NotImplemented()
    
    def get_nr_expired(self):
        """ Devuelve el número de procesos en el array expired."""
        raise NotImplemented()
    
    def get_nr_active(self):
        """ Devuelve el número de procesos en el array active."""
        raise NotImplemented()