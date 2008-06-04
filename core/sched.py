#!/usr/bin/python
# coding: utf-8
from sys import argv
from cpu import cpu
from task import task
import os
import const
from time import sleep

class scheduler():
    def __init__(self, n_cpus = 1):
        """ Inicializa un nuevo planificador"""
        print "Inicializando scheduler"
        self.cpus=[]
        while n_cpus:
            self.cpus.append(cpu(n_cpus))
            n_cpus -= 1
            
        self.tasks = []
        self.add_tasks(const.TASK_DIR)
        # Alguna tarea tiene que ser current. Como llamamos al scheduler inmediatamente, 
        # no problema en coger cualquiera para serlo.
        self.current = self.tasks[0]
        
        for c in self.cpus:
            c.start()
    
    def add_tasks(self, proc_dir):
        """ Añade todos los procesos de un directorio"""
        for dir, subdir, files in os.walk(proc_dir):
            tareas = [d for d in files if d.endswith(".tsk")]
        for t in tareas:
            tmp = task(os.path.join(proc_dir, t))
            print "Intentando crear tarea desde", os.path.join(proc_dir, t)
            self.tasks.append(tmp); # Se inserta el proceso en la lista global.

        print "Tareas de '%s' añadidas" % proc_dir
        print "Haciendo fork de las tareas"
        for t in self.tasks:
            self.do_fork(t)
            t.update_state()
        print "Tareas del sistema: ",len(self.tasks)
        #for t in self.tasks:
        #     print t

    def do_fork(self, task):
        """ Aquí se inicializan los datos del nuevo proceso"""
        # Atributos necesarios para el planificador
        # Inicializados según los valores de sched_fork() sched.c@1145
        task.state = const.state["RUNNING"]
        task.prio = None
        task.run_list = None
        task.array = None
        task.sleep_avg = None
        task.timestamp = self.cpus[0].clock
        task.last_ran = None
        task.activated = None
        task.policy = const.policy["NORMAL"]
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        task.time_slice = 100
        task.first_time_slice = 1
        task.rt_priority = None
        task.flags = 0
        
    def check_tasks(self):
        print "check_tasks"
        #  Por cada tarea durmiente, comprueba si su nuevo estado según
        #  la línea temporal es != durmiente. Si es así se llama a
        #  try_to_wake_up. (Con esto se emula una waitqueue).

        
    def scheduler_tick(self):
        print "Scheduler_tick"
        
    def schedule(self):
        print "schedule"
        
    def do_ticks(self, step):
        print "Avanzando %d tick(s)"% step
        while step:
            step-=1
            self.check_tasks()
            self.scheduler_tick()
            if self.current.flags == const.NEED_RESCHED:
                    self.current.flags = 0;
                    self.schedule()
            for c in self.cpus:
                c.tick()
        
    def run(self):
        print "Scheduler en ejecución"
        while True:
            self.step = 1
            self.do_ticks(self.step)
            sleep(1/const.HZ)
    
if __name__ == "__main__":
    if len(argv) != 2:
        sched = scheduler()
    else:
        sched = scheduler(int(argv[1]))
        
    sched.run()