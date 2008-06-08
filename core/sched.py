#!/usr/bin/python
# coding: utf-8
from sys import argv
from cpu import cpu
from task import task
import bitutils

from const import *
from eppli_exceptions import  *

import os
from time import sleep



class scheduler():
    def __init__(self, ruta_procesos):
        """ Inicializa un nuevo planificador"""
        print "Inicializando scheduler"
        self.cpu = cpu()
        self.tasks = []

        self.add_tasks(ruta_procesos)
        print "Número de tareas en el sistema: ",len(self.tasks)
        
        self.cpu.start()
        self.current = self.cpu.idle_task
        self.NEED_RESCHED = False
        self.did_sched = False # Para el GUI
    
    def add_tasks(self, proc_dir):
        """ Añade todos los procesos de un directorio, excepto el IDLE"""
        tareas = None
        for dir, subdir, files in os.walk(proc_dir):
            if dir == proc_dir:
                tareas = [d for d in files if d.endswith(".tsk") and d != TASK_IDLE]
                idle = [d for d in files if d == TASK_IDLE]
                print "Ficheros a considerar: %s" % tareas
        
        if not tareas or not idle:
            error = "'%s' no contiene tareas adecuadas o idle.tsk" % proc_dir
            raise NoTaskOrIdleDir(error)
        
        for t in tareas:
            tmp = task(os.path.join(proc_dir, t))
            print "Intentando crear tarea desde", os.path.join(proc_dir, t)
            self.tasks.append(tmp); # Se inserta el proceso en la lista global.

        for i in idle:
            print "Creando proceso IDLE de la CPU (%s)" % os.path.join(proc_dir, i)
            self.cpu.idle_task = task(os.path.join(proc_dir, i))
            self.cpu.init_idle_task(self.cpu.idle_task)
            self.cpu.rq.idle = self.cpu.idle_task

        print "Tareas de '%s' añadidas" % proc_dir
        print "Haciendo 'fork' de las tareas."
        for t in self.tasks:
            t.update_state()
            self.do_fork(t)

    def do_fork(self, task):
        task.state = state["RUNNING"]
        
        task.run_list = self.cpu.rq
        task.sleep_avg = 0
        task.prio = task.effective_prio()
        self.cpu.rq.active.add_task(task)
        task.array= self.cpu.rq.active
        self.cpu.rq.nr_running += 1
        task.time_slice = task.task_timeslice()
        
    def update_n_check_tasks(self):
        #  Por cada tarea, comprueba si su nuevo estado según
        #  la línea temporal es != durmiente. Si es así se llama a
        #  try_to_wake_up. (Con esto se emula una waitqueue).

        # current se incrementa manualmente para evitar que tareas en estado running
        # avancen su timeline sin tener realmente la CPU. Ver task.tick() 
        self.current.localtime+=1

        for t in self.tasks:
            #print "Comprobando tarea: ", t.name 
            t.tick()
            # El proceso ha dejado de estr en ejecución, se necesita llamar al scheduler
            if t.state != state["RUNNING"] and t.oldstate == state["RUNNING"]  and t.prio == self.cpu.rq.active:
                self.NEED_RESCHED = True
                continue
            
            if t.state == state["EXIT"]:
                self.NEED_RESCHED = True
                print "[%d] La tarea %s ha terminado!" % (self.cpu.clock, t.name)
                print "Tiempo en ejecución:", t.localtime
                print "Tiempo de ejecución:", self.cpu.clock
                continue
            
            if t.flags == NEED_RESCHED and t.state != state["EXIT"]:
                self.try_to_wake_up(t)

        if self.current.state != state["RUNNING"]:
            self.NEED_RESCHED = True
        
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
            print "[%d] La tarea %s ha agotado su timeslice..." % (cpu.clock, p.name)
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
            if not p.interactive() or rq.expired_starving():
                print "No interactiva o starving"
                rq.expired.add_task(p)
                if p.static_prio < rq.best_expired_prio:
                    rq.best_expired_prio = p.static_prio
            else:
                rq.active.add_task(p)

        else:
            p_interac = p.interactive()
            p_t_tl = p.task_timeslice()
            p_granu = p.timeslice_granularity()
            print "p_granu:", p_granu
            if (p_interac and not ((p_t_tl - p.time_slice) 
            % p_granu) and (p.time_slice >= p_granu) and
            (p.array == rq.active)):
                #print "Troceando el timeslice de %s: %d" %(p.name, p.time_slice)
                rq.active.del_task(p)
                rq.active.add_task(p)
                p.flags = NEED_RESCHED
                self.NEED_RESCHED = True
            
                
    def try_to_wake_up(self, t):
        print "try_to_wake_up: ", t.name
        c = self.cpu
        rq = self.cpu.rq
        if t.array:
            return
        if t.state == state["UNINTERRUPTIBLE"]:
            rq.nr_uninterruptible -= 1
            t.activated = -1
        
        self.activate_task(t)
        
        t.state = state["RUNNING"]
        
        t.flags = NEED_RESCHED
        self.NEED_RESCHED=True
        
        
    def activate_task(self, t):
        t.recalc_task_prio(self.cpu.clock)
        if not t.activated:
            t.activated = 2
        t.timestamp = self.cpu.clock
        
        # __activate_task
        self.cpu.rq.nr_running += 1
        self.cpu.rq.active.add_task(t)
        
    def schedule(self):
        print "schedule"
        #print "Procesos pendientes:", self.tasks
        prev = self.current
        rq = self.cpu.rq
        now = self.cpu.clock

        print "[%d] Proceso actual: %s" % (now, prev.name)
        
        if now - prev.timestamp < MAX_SLEEP_AVG:
            run_time = now - prev.timestamp
        else:
            run_time = MAX_SLEEP_AVG
        
        if prev.current_bonus():
            run_time /= prev.current_bonus()

        print "Estado de prev (%s): %d"  % (prev.name, prev.state)
        if prev.state != state["RUNNING"]:
            if prev.state == state["INTERRUPTIBLE"]:
                prev.state = state["RUNNING"]
            else:
                if prev.state == state["UNINTERRUPTIBLE"]:
                    rq.nr_uninterruptible+=1
                print "Desactivando la tarea", prev.name
                prev.deactivate()
                    
        if not rq.nr_running:
            print "Haciendo de IDLE el proceso next"
            next = rq.idle
            
        if not rq.active.nr_active:
            print "Intercambiando los arrays!"
            rq.active, rq.expired = rq.expired, rq.active
            rq.active.name="Active"
            rq.expired.name = "Expired"
            rq.expired_timestamp = 0
            rq.best_expired_prio = MAX_PRIO
            
        array = rq.active
        idx = bitutils.ffs(array.bitmap)
        print "Primer bit activo de %s (%d): %d" %(array.name, array.bitmap, idx)
        try:
            next = array.queue[idx][0]
        except KeyError:
            # Esta excepción se da si el índice idx es -1, es decir, 
            # el prio_array está vacio. Cambio a IDLE.
            next = self.cpu.idle_task
            
        print "Proceso next:", next.name
        
        if next.policy == policy["NORMAL"] and next.activated > 0:
            delta = now - next.timestamp
            if next.activated == 1:
                delta = delta * (ON_RUNQUEUE_WEIGHT * 128 / 100) / 128
            array = next.array
            array.del_task(next)
            next.recalc_task_prio(next.timestamp + delta)
            array.add_task(next)
        
        next.activated = 0
        
        prev.sleep_avg -= run_time
        if prev.sleep_avg <= 0:
            prev.sleep_avg = 0
        
        prev.timestamp = prev.last_ran = now

        if prev != next:
            next.timestamp = now
            rq.nr_switches+=1
            rq.curr = next
            if prev.state == state["EXIT"]:
                self.tasks.remove(prev)
                del prev

        self.current = next
        self.cpu.rq.current = next

        
    def do_ticks(self, step=1):

        # print "Avanzando %d tick(s)"% step
        while step:
            step-=1
            self.update_n_check_tasks()
            self.scheduler_tick()
            clock = self.cpu.clock
            
            if self.NEED_RESCHED:
                print "[%d] Se necesita resched!" % clock
            
            # Para que el GUI sepa que se ha ejecutado schedule()
            self.did_sched = False
            
            if self.NEED_RESCHED or clock % HZ == 0:
                    self.current.flags = 0;
                    self.NEED_RESCHED = False
                    self.did_sched = True
                    self.schedule()
            
            self.cpu.tick()
            
        return len(self.tasks)
                    
    def run(self):
        print "Scheduler en ejecución"
        while len(self.tasks):
            if self.cpu.running:
                self.do_ticks(1)
                sleep(1/HZ)
    
if __name__ == "__main__":
    sched = scheduler(TASK_DIR)
    sched.run()