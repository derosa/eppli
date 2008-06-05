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
        print "Prio array creado."
    
    def add_task(self, t):
        try:
            self.queue[t.prio].append(t)
            print "rq %s :: Añadiendo tarea: %s" % (self.name, t.name)
        except KeyError:
            print "Error con la clave :("
            print "rq %s :: Añadiendo tarea: %s" % (self.name, t.name)
            self.queue[t.prio] = []
            self.queue[t.prio].append(t)
            
        bitutils.set_bit(self.bitmap, t.prio)
        self.nr_active+=1
        t.array = self
        print "Cola %s :: %s" % (self.name, self.queue)
    
    def del_task(self, t):
        idx = None
        try:
            idx = self.queue[t.prio].index(t)
        except:
            print "El proceso %s (%d) no existe en la rq %s" % (t.name, t.prio, self.name)
            print " contenido de la rq: ", self.queue

        if idx:
            print "rq %s :: Eliminando tarea: %s" % (self.name, t)
            self.nr_active-=1
            del self.queue[t.prio][idx]
            t.array = None
            if not len(self.queue[t.prio]):
                print "rq %s :: Prioridad %d vacía, eliminando" % (self.name, t.prio)
                bitutils.clear_bit(self.bitmap, t.prio)
                del self.queue[t.prio]

    