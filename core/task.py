# coding:utf-8
""" Clase para representar tareas del planificador"""
import const

class Task():
    """ Un tarea a partir de un archivo de texto descriptivo"""
    def __init__(self, source):
        """ Crea una nueva tarea a partir de un archivo de texto
        el formato del archivo es:
        ^NAME=nombre del proceso$
        ^[0-9]*=[IOWAIT|RUNNING|EXIT]$"""
        
        # Atributos para el emulador
        self.timeline = {}
        self.name = ""
        self.localtime = 0

        # Atributos necesarios para el planificador
        self.state = const.NEED_RESCHED
        self.prio = 0
        self.run_list = 0
        self.array = 0
        self.sleep_avg = 0
        self.timestamp = 0
        self.last_ran = 0
        self.activated = 0
        self.policy = const.NORMAL
        self.time_slice = 0
        self.first_time_slice = 1
        self.rt_priority = 0

        
        try: 
            self.fill_timeline(source)
        except IOError:
            print "Error al procesar la tarea de fuente %s" % source
            return None
        
    def fill_timeline(self, source):
        """Genera una línea de tiempo de ejecución del proceso a partir del
        archivo que se le pasa."""

        fsource = open(source, "r")

        for linea in fsource:
            if linea.startswith("NAME"):
                self.name = linea.split("=")[1]
                print "Creando proceso %s" % self.name
            else:
                tmp = linea.split("=")
                when = int(tmp[0])
                what = tmp[1].strip()
                self.timeline[when] = what

    def update_state(self):
        if self.localtime in self.timeline:
            self.oldstate = self.state
            self.state = self.timeline[self.localtime]
            
            

if __name__ == "__main__":
    tmp = Task("task1.tsk")
    print "Nombre: %s" % tmp.name
    print "Linea temporal: ", tmp.timeline