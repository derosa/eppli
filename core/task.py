# coding:utf-8
""" Clase para representar tareas del planificador"""
from const import *
from time import sleep

class task():
    """ Un tarea a partir de un archivo de texto descriptivo"""
    def __init__(self, source):
        """ Crea una nueva tarea a partir de un archivo de texto. 
        Asumimos que todas las tareas comienzan en el estado RUNNING
        El formato del archivo es:
        ^NAME=nombre del proceso$
        ^PRIO=[0-9]*$
        ^CLASS=FIFO|RR|NORMAL
        ^[0-9]*=[INTERRUPTIBLE|UNINTERRUPTIBLE|RUNNING|EXIT]$"""
        
        print "Iniciando tarea desde fuente:", source
        # Atributos para el emulador
        self.timeline = {}
        self.name = ""
        self.localtime = 0
        self.state = state["RUNNING"]
        self.oldstate = self.state
        self.static_prio = 0
        self.prio = 0
        self.run_list = None
        self.array = None 
        self.sleep_avg = 0
        self.timestamp = 0
        self.last_ran = 0
        self.activated = 0
        self.policy = policy["NORMAL"]
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        self.time_slice = 100
        self.first_time_slice = 1
        self.rt_priority = 0
        self.flags = 0
        
        try: 
            self._fill_timeline(source)
        except IOError:
            print "Error al procesar la tarea de fuente %s" % source
            return None

    def __str__(self):
        """ Representación en texto de una tarea"""
        tmp =""
        tmp += "Nombre: %s\n" % self.name
        tmp += "Prioridad: %d\n" % self.static_prio
        tmp += "Clase: %d\n" % self.policy
        tmp += "Linea temporal: %s\n" % self.timeline
        tmp += "Estado: %d\n" % self.state
        return tmp
            
    def _fill_timeline(self, source):
        """Genera una línea de tiempo de ejecución del proceso a partir del
        archivo que se le pasa."""

        fsource = open(source, "r")
        
        for linea in fsource:
            tmp = linea.split("=")
            if tmp[0] == "NAME":
                self.name = tmp[1].strip()
            elif tmp[0] == "PRIO":
                self.static_prio = int(tmp[1].strip())
                self.prio =self.effective_prio()
            elif tmp[0] == "CLASS":
                self.policy = policy[tmp[1].strip()]
            else:
                when = int(tmp[0])
                what = tmp[1].strip()
                self.timeline[when] = what

    def update_state(self):
        """ Comprueba el estado del proceso y lo actualiza si ha cambiado"""
        self.oldstate = self.state
        if self.localtime in self.timeline and state[self.timeline[self.localtime]] != self.state:
            self.state = state[self.timeline[self.localtime]]
            self.flags = NEED_RESCHED
            print "%s[%d]: Cambio de estado: %s -> %s" % (self.name, self.localtime, self.oldstate, self.state)
        else:
            self.flags = None
        
    def tick(self):
        self.update_state()
        # Solo actualizamos la hora para saber si pasamos a estar activos.
        # Si actualizara también en RUNNING, parecería que hemos tenido la CPU
        # sin tenerla, pues no somos "current"
        if self.state != state["RUNNING"]:
            self.localtime+=1
        
    def task_timeslice(self):
        if self.static_prio < 120:
            x = DEF_TIMESLICE*4
        else:
            x = DEF_TIMESLICE
        ret = max ( x*(MAX_PRIO-self.prio) / (MAX_USER_PRIO/2), MIN_TIMESLICE)
        print "Nuevo timeslice de %s: %d" % (self.name, ret)
        return ret
    
    def effective_prio(self):
        # Devuelve la prioridad efectiva.
        bonus = self.current_bonus() - MAX_BONUS/2
        return self.static_prio - bonus
    
    def current_bonus(self):
        ret = self.sleep_avg * MAX_BONUS / MAX_SLEEP_AVG
        return ret
    
    def interactive(self):
        # Indica si la tarea es interactiva
        return self.prio <= (self.static_prio - self.delta())
    
    def interactive_sleep(self):
    #58#define PRIO_TO_NICE(prio)      ((prio) - MAX_RT_PRIO - 20)
    #59#define TASK_NICE(p)            PRIO_TO_NICE((p)->static_prio)
    #91#define INTERACTIVE_DELTA         2
    #139#define SCALE(v1,v1_max,v2_max) \
    #140        (v1) * (v2_max) / (v1_max)
    #141
    #142#define DELTA(p) \
    #143        (SCALE(TASK_NICE(p), 40, MAX_BONUS) + INTERACTIVE_DELTA)
    #148#define INTERACTIVE_SLEEP(p) \
    #149        (JIFFIES_TO_NS(MAX_SLEEP_AVG * \
    #150                (MAX_BONUS / 2 + DELTA((p)) + 1) / MAX_BONUS - 1))
       ret = (MAX_SLEEP_AVG * (MAX_BONUS/2 + self.delta() +1) / MAX_BONUS - 1)
       return ret
   
    def delta(self):
        # 58#define PRIO_TO_NICE(prio)      ((prio) - MAX_RT_PRIO - 20)
        # 59#define TASK_NICE(p)            PRIO_TO_NICE((p)->static_prio)
        # 139#define SCALE(v1,v1_max,v2_max) \
        # 140        (v1) * (v2_max) / (v1_max)
        # 141
        # 142#define DELTA(p) \
        # 143        (SCALE(TASK_NICE(p), 40, MAX_BONUS) + INTERACTIVE_DELTA)
        tn = self.static_prio - MAX_RT_PRIO - 20
        escala = tn * MAX_BONUS / 40

        return escala + INTERACTIVE_DELTA
    
    def recalc_task_prio(self, now):

        sleep_time = min(now - self.timestamp, MAX_SLEEP_AVG)

        if sleep_time:
            if self.activated == -1 and sleep_time > self.interactive_sleep():
                self.sleep_avg = MAX_SLEEP_AVG - DEF_TIMESLICE
            else:
                sleep_time *= max(MAX_BONUS - self.current_bonus(), 1)
                if self.activated == -1:
                    if self.sleep_avg >= self.interactive_sleep():
                        self.sleep_avg = self.interactive_sleep()
                        sleep_time = 0
                
                self.sleep_avg+=sleep_time
                
                if self.sleep_avg > MAX_SLEEP_AVG:
                    self.sleep_avg = MAX_SLEEP_AVG
        
        self.prio = self.effective_prio()
                   

    def timeslice_granularity(self):
        #135#define TIMESLICE_GRANULARITY(p) (GRANULARITY * \
        #136                (1 << (((MAX_BONUS - CURRENT_BONUS(p)) ? : 1) - 1)))
        ret = GRANULARITY * (1 << (MAX_BONUS - self.current_bonus()))
        return ret

    def deactivate(self):
        self.run_list.nr_running -= 1
        print "%s.deactivate()" % self.name
        self.array.del_task(self)
        self.array = None
                
if __name__ == "__main__":
    tmp = task("tasks/task1.tsk")
    print tmp
    print "Demo de ejecución y cambio de estado"
    while tmp.state != state["EXIT"]:
        print "Tick: ", tmp.localtime
        tmp.tick()
        sleep(0.1/HZ)
