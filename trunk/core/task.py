# coding:utf-8
""" Clase para representar tareas del planificador"""
import const

class task():
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
            if linea.startswith("NAME"):
                self.name = linea.split("=")[1]
                print "Creando proceso %s" % self.name
            else:
                tmp = linea.split("=")
                when = int(tmp[0])
                what = tmp[1].strip()
                self.timeline[when] = what

    def update_state(self):
        """ Comprueba el estado del proceso y lo actualiza si ha cambiado"""
        if self.localtime in self.timeline:
            self.oldstate = self.state
            self.state = self.timeline[self.localtime]
            self.state = const.NEED_RESCHED
            
            

if __name__ == "__main__":
    tmp = Task("task1.tsk")
    print "Nombre: %s" % tmp.name
    print "Linea temporal: ", tmp.timeline