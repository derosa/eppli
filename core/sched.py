#!/usr/bin/python
# coding: utf-8
from sys import argv
from cpu import cpu
from task import task

from const import *

import os
from time import sleep

class scheduler():
    def __init__(self, n_cpus = 1):
        """ Inicializa un nuevo planificador"""
        print "Inicializando scheduler"
        
        self.cpu = cpu(n_cpus)
            
        self.tasks = []
        self.add_tasks(TASK_DIR)

        # Alguna tarea tiene que ser current. Como llamamos al scheduler inmediatamente, 
        # no problema en coger cualquiera para serlo.
        self.current = self.tasks[0]
        
        self.cpu.start()
    
    def add_tasks(self, proc_dir):
        """ Añade todos los procesos de un directorio, excepto el IDLE"""
        for dir, subdir, files in os.walk(proc_dir):
            if dir == proc_dir:
                tareas = [d for d in files if d.endswith(".tsk") and not d.startswith("idle")]
                print "Ficheros a considerar: %s" % tareas
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
        self.cpu.rq.active.add_task(task)
        
    def update_n_check_tasks(self):
        #print "update_n_check_tasks:"
        #if len(self.tasks)==1:
        #    print self.tasks[0]
        
        #  Por cada tarea, comprueba si su nuevo estado según
        #  la línea temporal es != durmiente. Si es así se llama a
        #  try_to_wake_up. (Con esto se emula una waitqueue).

        # current se incrementa manualmente para evitar que tareas en estado running
        # avancen su timeline sin tener realmente la CPU 
        self.current.localtime+=1

        for t in self.tasks:
            #print "Comprobando tarea: ", t.name 
            t.tick()
            # El proceso ya no está en ejecución, se saca de la rq de procesos activos
            if t.oldstate == state["RUNNING"] and t.state != state["RUNNING"] and t.prio == self.cpu.rq.active:
                self.cpu.rq.active.del_task(t)
            
            if t.state == state["EXIT"]:
                self.NEED_RESCHED = True
                print "La tarea %s ha terminado!" % t.name
                print "Tiempo de ejecución:", t.localtime
                # Saco la tarea de la rq:
                t.array.del_task(t)
                del self.tasks[self.tasks.index(t)]
                continue
            if t.flags == NEED_RESCHED:
                self.try_to_wake_up(t)

        if self.current.state != state["RUNNING"]:
            self.NEED_RESCHED = True
            
        need_idle = [i for i in self.tasks if i.state == state["RUNNING"]]
        # print "Procesos activos: ", len(need_idle)
        self.cpu.rq.nr_running = len(need_idle)
        if not len(need_idle):
            print "Conmutando a IDLE!"
            self.current = self.cpu.idle_task
            self.cpu.rq.current = self.current
            
        
    def scheduler_tick(self):
        # print "Scheduler_tick"
        cpu = self.cpu  
        rq = cpu.rq
        p = self.current
        rq.timestamp_last_tick = cpu.clock
        
        if self.current == cpu.idle_task:
            return
        
        if p.array != cpu.rq.active:
            self.NEED_RESCHED = True
            return

        p.time_slice-=1
        
        # Si es una tarea de tiempo real...
        if p.policy < policy["NORMAL"]:
            if p.policy == policy["RR"] and not p.time_slice:
                p.time_slice = p.task_timeslice()
                p.first_time_slice = 0
                self.NEED_RESCHED = True
                # Coloco el proceso al final de la lista (RR)
                rq.active.del_task(p)
                rq.active.add_task(p)
            return
        
        # Si la tarea agota su timeslice...
        if not p.time_slice:
            rq.active.del_task(p)
            self.NEED_RESCHED = True
            p.flags = self.NEED_RESCHED
            p.prio = p.effective_prio()
            p.time_slice = p.task_timeslice()
            p.first_time_slice = 0
            if rq.expired_timestamp == 0:
                rq.expired_timestamp = cpu.clock
            # si no es interactiva o hay cosas sin ejecutarse mucho tiempo,
            # a la cola de expirados
            if not p.interactive() or rq.expired.starving():
                print "No interactiva o starving"
                rq.expired.add_task(p)
                if p.static_prio < rq.best_expired_prio:
                    rq.best_expired_prio = p.static_prio
            else:
                rq.active.add_task(p)
                
        # Comprueba que la tarea actual no lleva demasiado tiempo en ejecución
        # y divide su timeslice en porciones más pequeñas.
# 2487                if (TASK_INTERACTIVE(p) && !((task_timeslice(p) -
#2488                        p->time_slice) % TIMESLICE_GRANULARITY(p)) &&
#2489                        (p->time_slice >= TIMESLICE_GRANULARITY(p)) &&
#2490                        (p->array == rq->active)) {
#2491
#2492                        requeue_task(p, rq->active);
#2493                        set_tsk_need_resched(p);
#2494                }
        else:
            if (p.interactive() and not ((p.task_timeslice() - p.time_slice) 
            % p.timeslice_granularity()) and (p.time_slice >= p.timeslice_granularity()) and
            (p.array == rq.active)):
                rq.active.del_task(p)
                rq.active.add_task(p)
                p.flags = NEED_RESCHED
                self.NEED_RESCHED = True
            
                
    def try_to_wake_up(self, t):
        print "Intentando levantar: ", t.name
        c = self.cpu
        rq = self.cpu.rq
        if t.array:
            return
        if t.state == state["UNINTERRUPTIBLE"]:
            rq.nr_uninterruptible -= 1
            p.activated = -1
        
        activate_task(t)
        
        p.state = state["RUNNING"]
        
        
    def activate_task(self, t):
        t.recalc_task_prio()
        if not p.activated:
            p.activated = 2
        p.timestamp = self.cpu.clock
        
        # __activate_task
        self.cpu.rq.nr_running += 1
        self.cpu.rq.active.add_tsk(t)
        self.cpu.rq.active.active += 1
        p.array = self.cpu.rq.active
        
        
    def schedule(self):
        print "schedule"
        print "Procesos pendientes:", self.tasks

    def do_ticks(self, step):

        # print "Avanzando %d tick(s)"% step
        while step:
            step-=1
            self.update_n_check_tasks()
            self.cpu.tick()
            self.scheduler_tick()
            clock = self.cpu.clock

            if self.current.flags == NEED_RESCHED or clock % HZ == 0:
                    self.current.flags = 0;
                    self.schedule()
            
            sleep(0.01/HZ)
                
                    
    def run(self):
        print "Scheduler en ejecución"
        while len(self.tasks):
            self.step = 1
            self.do_ticks(self.step)
            #sleep(0.01/HZ)
    
if __name__ == "__main__":
    if len(argv) != 2:
        sched = scheduler()
    else:
        sched = scheduler(int(argv[1]))
        
    sched.run()