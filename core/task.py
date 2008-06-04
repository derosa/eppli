# coding:utf-8
""" Clase para representar tareas del planificador"""
import const

class task():
    """ Un tarea a partir de un archivo de texto descriptivo"""
    def __init__(self, source):
        """ Crea una nueva tarea a partir de un archivo de texto
        el formato del archivo es:
        ^NAME=nombre del proceso$
        ^PRIO=[0-9]*$
        ^CLASS=FIFO|RR|NORMAL
        ^[0-9]*=[INTERRUPTIBLE|UNINTERRUPTIBLE|RUNNING|EXIT]$"""
        
        # Atributos para el emulador
        self.timeline = {}
        self.name = ""
        self.localtime = 0
        
        try: 
            self._fill_timeline(source)
        except IOError:
            print "Error al procesar la tarea de fuente %s" % source
            return None
        
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
        		self.policy = tmp[1].strip()
        	else:
				when = int(tmp[0])
				what = tmp[1].strip()
				self.timeline[when] = what

    def update_state(self):
        """ Comprueba el estado del proceso y lo actualiza si ha cambiado"""
        if self.localtime in self.timeline:
            self.oldstate = self.state
            self.state = self.timeline[self.localtime]
            self.flags = const.NEED_RESCHED
            
            

if __name__ == "__main__":
    tmp = task("task1.tsk")
    print "Nombre: %s" % tmp.name
    print "Prioridad:", tmp.static_prio
    print "Clase:", tmp.policy
    print "Linea temporal: ", tmp.timeline
