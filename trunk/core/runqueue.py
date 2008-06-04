# coding: utf-8

from prio_array import prio_array
import const

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
        
        print "Priority Arrays creados"
        
    def starving(self):
        s = const.STARVATION_LIMIT and self.expired_timestamp \
        and (cpu.clock - self.expired_timestamp >=  consts.STARVATION_LIMIT * 
        this.nr_running + 1) or (this.current.static_prio > this.best_expired_prio)
        return s
