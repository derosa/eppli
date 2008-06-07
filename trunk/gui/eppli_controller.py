#/usr/bin/python
#coding: utf-8

class NotImplemented(Exception): pass

class eppli_controller():
    def __init__(self, parent):
        """ Inicia el controlador que controlará a 'parent' """
        print "Iniciando controlador de EPPLI"
        self.view = parent
        
    def new_scheduler(self, ruta_tasks):
        """ Inicia un nuevo scheduler con las tareas de ruta_tasks"""
        raise NotImplemented()
    
    def del_scheduler(self):
        """ Elimina los datos del scheduler """
        raise NotImplemented()
    
    def sched_step(self, steps=1):
        """ Avanza un paso en el planificador"""
        raise NotImplemented() 
    
    def get_current(self):
        """ Devuelve la tarea current del sistema """
        raise NotImplemented()
    
    def get_tasks(self, name):
        """ Devuelve la tarea de nombre name """
        raise NotImplemented()
    
    def get_sched_stats(self):
        """ Devuelve las estadísticas del planificador """
        raise NotImplemented()
    
    def _get_bitmap(self, name):
        """ Devuelve el bitmap del array solicitado"""
        raise NotImplemented()
    
    def get_bitmap_active(self):
        """ Devuelve un array de bits representando al bitmap del array active"""
        raise NotImplemented()
    
    def get_bitmap_expired(self):
        """ Devuelve un array de bits representando al bitmap del array expired"""
        raise NotImplemented()
    
    def get_nr_expired(self):
        """ Devuelve el número de procesos en el array expired"""
        raise NotImplemented()
    
    def get_nr_active(self):
        """ Devuelve el número de procesos en el array active"""
        raise NotImplemented()