# coding: utf-8

from prio_array import prio_array

class runqueue():
    def __init__(self, CPU):
        self.cpu = CPU
        self.active = prio_array()
        self.expired = prio_array()