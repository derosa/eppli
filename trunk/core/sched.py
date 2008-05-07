#!/usr/bin/python
# coding: utf-8
from sys import argv

from cpu import cpu

class scheduler():
    def __init__(self, n_cpus = 1):
        """ Inicializa un nuevo planificador"""
        self.cpus=[]
        
        while n_cpus:
            self.cpus.append(cpu(n_cpus))
            n_cpus -= 1
        for c in self.cpus:
            c.start()
    
    def add_tasks(self, proc_dir):
        """ Añade todos los procesos de un directorio"""
        
    def do_fork(self, task):
        """ Aquí se inicializan los datos del nuevo proceso"""

        # Atributos necesarios para el planificador
        # Inicializados según los valores de sched_fork() sched.c@1145
        task.state = const.RUNNING
        task.prio = None
        task.run_list = None
        task.array = None
        task.sleep_avg = None
        task.timestamp = cpus[0].clock
        task.last_ran = None
        task.activated = None
        task.policy = const.NORMAL
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        task.time_slice = 100
        task.first_time_slice = 1
        task.rt_priority = None
        
    
if __name__ == "__main__":
    if len(argv) != 2:
        sched = scheduler()
    else:
        sched = scheduler(int(argv[1]))