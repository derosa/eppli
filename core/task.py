# coding:utf-8
""" Clase para representar tareas del planificador"""
import const
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
        self.localtime = -1
        self.state = None
        self.prio = 0
        self.static_prio = 0
        self.run_list = None
        self.array = None 
        self.sleep_avg = None
        self.timestamp = None
        self.last_ran = None
        self.activated = None
        self.policy = const.policy["NORMAL"]
        # En sched_fork() se asigna la mitad del timeslice del proceso padre, 
        # del que carecemos, por lo que uso un time_slice por defecto.
        self.time_slice = 100
        self.first_time_slice = 1
        self.rt_priority = None
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
            elif tmp[0] == "CLASS":
                self.policy = const.policy[tmp[1].strip()]
            else:
                when = int(tmp[0])
                what = tmp[1].strip()
                self.timeline[when] = what

    def update_state(self):
        """ Comprueba el estado del proceso y lo actualiza si ha cambiado"""
        if self.localtime in self.timeline and const.state[self.timeline[self.localtime]]  != self.state:
            self.oldstate = self.state
            self.state = const.state[self.timeline[self.localtime]]
            self.flags = const.NEED_RESCHED
            print "%s[%d]: Cambio de estado: %s -> %s" % (self.name, self.localtime, self.oldstate, self.state)
        self.flags = None
        
    def tick(self):
        self.update_state()
        self.localtime+=1
        
    def task_timeslice(self):
        ## TODO: Rellenar esta funcion
        return 100
    
    def effective_prio(self):
        ## TODO Devuelve la prioridad efectiva.
        return 100
    
    def interactive(self):
        # TODO: Indica si la tarea es interactiva
        return False

    def recalc_task_prio(self):
        # TODO: Rellenar esta función :P
        self.prio = self.static_prio


if __name__ == "__main__":
    tmp = task("tasks/task1.tsk")
    print tmp
    
    print "Demo de ejecución y cambio de estado"
    while tmp.state != const.state["EXIT"]:
        print "Tick: ", tmp.localtime
        tmp.tick()
        sleep(0.1/const.HZ)

        
