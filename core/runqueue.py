# coding: utf-8

from prio_array import prio_array
from const import *

class runqueue():
    def __init__(self, CPU):
        """ Inicializa una runqueue. Se pasa la CPU a la que pertenece"""
        self.cpu = CPU
        print "Iniciando runqueue de la CPU", self.cpu.id
        self.active = prio_array()
        self.active.name="Active" # Para depurar
        self.expired = prio_array()
        self.expired.name="Expired" # Para depurar
        self.expired_timestamp = 0
        self.nr_running = 0
        self.current = None
        self.best_expired_prio = 0
        self.nr_interruptible = 0
        self.nr_uninterruptible = 0
        self.nr_switches = 0
        
        print "Priority Arrays creados"
        
    def expired_starving(self):
        s1 = STARVATION_LIMIT and self.expired_timestamp \
            and (self.cpu.clock - self.expired_timestamp >= STARVATION_LIMIT * 
                 self.nr_running + 1)
        s2 = self.current.static_prio > self.best_expired_prio
        #print "starving: s1: %d, s2 (%d > %d): %d" % (s1, self.current.static_prio, self.best_expired_prio, s2)
        return s1 or s2
