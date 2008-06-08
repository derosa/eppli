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
        #print "Prio array creado."
    
    def add_task(self, t):
        #print "prio_array %s :: Añadiendo tarea: %s[%d]" % (self.name, t.name, t.prio)
        try:
            self.queue[t.prio].append(t)
        except KeyError:
            #print "Error con la clave :("
            self.queue[t.prio] = []
            self.queue[t.prio].append(t)
            
        #print "Cola %s :: Activando bit %d en %d" % (self.name, t.prio, self.bitmap)
        self.bitmap = bitutils.set_bit(self.bitmap, t.prio)
        self.nr_active+=1
        t.array = self
        #print "Cola %s :: bitmap: %d" % (self.name, self.bitmap)
        #print "Cola %s :: procesos : %s" % (self.name, self.queue)
        
    
    def del_task(self, t):
        idx = None
        try:
            idx = self.queue[t.prio].index(t)
        except:
            #print "El proceso %s (%d) no existe en la prio_array %s!!!" % (t.name, t.prio, self.name)
            #print " contenido de la queue: ", self.queue
            return

        #print "prio_array %s :: Eliminando tarea: %s[%d]" % (self.name, t.name, t.prio)
        self.nr_active-=1
        del self.queue[t.prio][idx]
        t.array = self
        if not len(self.queue[t.prio]):
            #print "prio_array %s :: Prioridad %d vacía, eliminando" % (self.name, t.prio)
            self.bitmap = bitutils.clear_bit(self.bitmap, t.prio)
            del self.queue[t.prio]
        
        #print "prio_array %s :: Tarea %s eliminada, nueva queue: %s" % (self.name, t.name, self.queue)