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
        
        self.cpu = cpu(n_cpus)
            
        self.tasks = []
        self.add_tasks(const.TASK_DIR)
        # Alguna tarea tiene que ser current. Como llamamos al scheduler inmediatamente, 
        # no problema en coger cualquiera para serlo.
        self.current = self.tasks[0]
        
        self.cpu.start()
    
    def add_tasks(self, proc_dir):
        """ Añade todos los procesos de un directorio, excepto el IDLE"""
        for dir, subdir, files in os.walk(proc_dir):
            tareas = [d for d in files if d.endswith(".tsk") and not d.startswith("idle")]
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
        task.prio = task.static_prio
        task.run_list = self.cpu.rq
        task.array = self.cpu.rq.active
        task.sleep_avg = None
        task.timestamp = self.cpu.clock
        task.last_ran = None
        task.activated = None
        task.policy = const.policy["NORMAL"]
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        task.time_slice = 100
        task.first_time_slice = 1
        task.rt_priority = None
        task.flags = 0
        
        self.cpu.rq.active.add_task(task)
        
    def update_n_check_tasks(self):
        print "update_n_check_tasks:"
        if len(self.tasks)==1:
            print self.tasks[0]
        #  Por cada tarea, comprueba si su nuevo estado según
        #  la línea temporal es != durmiente. Si es así se llama a
        #  try_to_wake_up. (Con esto se emula una waitqueue).
        for t in self.tasks:
            print "Comprobando tarea: ", t.name 
            t.tick()
            if t.state == const.state["EXIT"]:
                self.NEED_RESCHED = True
                print "La tarea %s ha terminado!" % t.name
                print "Tiempo de ejecución:", t.localtime
                del self.tasks[self.tasks.index(t)]
                continue
            if t.flags == const.NEED_RESCHED:
                self.try_to_wake_up(t)

        if self.current.state != const.state["RUNNING"]:
            self.NEED_RESCHED = True
            
        need_idle = [i for i in self.tasks if i.state == const.state["RUNNING"]]
        print "Procesos activos: ", len(need_idle)
        self.cpu.rq.nr_running = len(need_idle)
        if not len(need_idle):
            print "Conmutando a IDLE!"
            self.current = self.cpu.idle_task
            this.cpu.rq.current = self.current
            
        
    def scheduler_tick(self):
        print "Scheduler_tick"
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
        if p.policy < const.policy["NORMAL"]:
            if p.policy == const.policy["RR"] and not p.time_slice:
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
                rq.expired.add_task(p)
                if p.static_prio < rq.best_expired_prio:
                    rq.best_expired_prio = p.static_prio
            else:
                rq.active.add_task(p)
                
                ## TODO
    def try_to_wake_up(self, t):
        print "Intentando levantar: ", t.name
        
    def schedule(self):
        print "schedule"
        self.cpu.rq.current = self.current

    def do_ticks(self, step):

        print "Avanzando %d tick(s)"% step
        while step:
            step-=1
            self.update_n_check_tasks()

            self.cpu.tick()
            
            self.scheduler_tick()

            clock = self.cpu.clock

            if self.current.flags == const.NEED_RESCHED or clock % const.HZ == 0:
                    self.current.flags = 0;
                    self.schedule()
            
            sleep(0.01/const.HZ)
                
                    
    def run(self):
        print "Scheduler en ejecución"
        while len(self.tasks):
            self.step = 1
            self.do_ticks(self.step)
            #sleep(0.01/const.HZ)
    
if __name__ == "__main__":
    if len(argv) != 2:
        sched = scheduler()
    else:
        sched = scheduler(int(argv[1]))
        
    sched.run()