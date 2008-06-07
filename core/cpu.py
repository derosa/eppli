# coding utf-8
from const import *
from prio_array import prio_array
from runqueue import runqueue
from task import task
from prio_array import prio_array


class cpu():
    def __init__(self, id=1):
        """ Inicializa una nueva CPU con todas sus estructuras"""
        print "Inicializando CPU", id
        self.id = id
        self.clock = 0
        self.rq = runqueue(self)
        
    def init_idle_task(self, task):
        task.state = state["RUNNING"]
        task.prio = 0
        task.run_list = self.rq
        task.array = self.rq.active
        task.sleep_avg = 0
        task.timestamp = self.clock
        task.last_ran = 0
        task.activated = 0
        task.policy = policy["NORMAL"]
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        task.time_slice = 100
        task.first_time_slice = 1
        task.rt_priority = 0
        task.flags = 0
        
    def start(self):
        print "CPU %d activada" % self.id
        self.running = True
        
    def stop(self):
        self.running = False
        
    def tick(self):
        if self.running:
            self.clock+=1
            #print "CPU(%d)[%d]: tick!" % (self.id, self.clock)