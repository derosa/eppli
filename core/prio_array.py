#coding: utf-8

from task import task
import bitutils

class prio_array():
    def __init__ (self):
        self.nr_active = 0
        self.bitmap = 0
        ## "queue" es de tipo list_head en el  kernel.
        ## Implemento como una tupla por las operaciones de inserción y eliminado rápido.
        self.queue={}
        print "Prio array creado"
    
    def add_task(self, t):
        print "rq %s :: Añadiendo tarea: %s" % (self.name, t)
        try:
            self.queue[t.prio].append(t)
        except KeyError:
            print "Error con la clave :("
            self.queue[t.prio] = []
            self.queue[t.prio].append(t)
            
        bitutils.set_bit(self.bitmap, t.prio)
        self.nr_active+=1
    
    def del_task(self, t):
        print "rq %s :: Eliminando tarea: %s" % (self.name, t)
        self.nr_active-=1
        index = self.queue[t.prio].index(t)
        del self.queue[t.prio][index]
        if not len(self.queue[t.prio]):
            bitutils.clear_bit(self.bitmap, t.prio)
            del self.queue[t.prio]
    
    