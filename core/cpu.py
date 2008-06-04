# coding utf-8
import const

from prio_array import prio_array
from runqueue import runqueue
from task import task
from prio_array import prio_array

class cpu():
    def __init__(self, id):
        """ Inicializa una nueva CPU con todas sus estructuras"""
        print "Inicializando CPU", id
        self.id = id
        self.clock = 0
        self.rq = runqueue(self)

    def start(self):
        print "CPU %d activada" % self.id
        self.running = True
    def stop(self):
        self.running = False
        
    def tick(self):
        if self.running:
            self.clock+=1
            print "CPU(%d)[%d]: tick!" % (self.id, self.clock)