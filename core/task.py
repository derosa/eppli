# coding:utf-8
""" Clase para representar tareas del planificador"""
import const
from time import sleep

class task():
    """ Un tarea a partir de un archivo de texto descriptivo"""
    def __init__(self, source):
        """ Crea una nueva tarea a partir de un archivo de texto
        el formato del archivo es:
        ^NAME=nombre del proceso$
        ^PRIO=[0-9]*$
        ^CLASS=FIFO|RR|NORMAL
        ^[0-9]*=[INTERRUPTIBLE|UNINTERRUPTIBLE|RUNNING|EXIT]$"""
        print "Iniciando tarea desde fuente:", source
        # Atributos para el emulador
        self.timeline = {}
        self.name = ""
        self.localtime = 0
        self.state = None
        
        try: 
            self._fill_timeline(source)
        except IOError:
            print "Error al procesar la tarea de fuente %s" % source
            return None

    def __str__(self):
        tmp =""
        tmp += "Nombre: %s\n" % self.name
        tmp += "Prioridad: %d\n" % self.static_prio
        tmp += "Clase: %d\n" % self.policy
        tmp += "Linea temporal: %s\n" % self.timeline
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
            print "%d: Cambio de estado: %s -> %s" % (self.localtime, self.oldstate, self.state)
            
    def tick(self):
        self.update_state()
        self.localtime+=1
            

if __name__ == "__main__":
    tmp = task("task1.tsk")
    print "Nombre: %s" % tmp.name
    print "Prioridad:", tmp.static_prio
    print "Clase:", tmp.policy
    print "Linea temporal: ", tmp.timeline
    
    print "Demo de ejecución y cambio de estado"
    while tmp.state != const.state["EXIT"]:
        print "Tick: ", tmp.localtime
        tmp.tick()
        sleep(0.1/const.HZ)

        
