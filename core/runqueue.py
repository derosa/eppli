# coding: utf-8

from prio_array import prio_array

class runqueue():
    def __init__(self, CPU):
        """ Inicializa una runqueue. Se pasa la CPU a la que pertenece"""
        self.cpu = CPU
        print "Iniciando runqueue de la CPU", self.cpu.id
        self.active = prio_array()
        self.expired = prio_array()
        print "Priority Arrays creados"