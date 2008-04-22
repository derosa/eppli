#coding: utf-8

from task import task

class prio_array():
    def __init__ (self):
        self.nr_active = 0
        self.bitmap = 0
        ## "queue" es de tipo list_head en el  kernel.
        ## Implemento como un "set" por las operaciones de inserción y eliminado rápido.
        self.queue=()
    
    def addTask(t):
            self.bitmap