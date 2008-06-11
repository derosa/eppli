#coding:utf-8

class sched_stats():
    """ Esta clase guarda estadísticas de procesos y el scheduler
    debe actualizarse con cada llamada a schedule()"""
    def __init__(self):
        # Mapa de procesos. Las estadísticas se guardarán de esta forma:
        # procs[NOMBRE_PROCESO].append((tick, prio, timeslice, completado))
        self.tasks = {}
        # Cambios de contexto en el tiempo:
        # sched_switches[TICK]=NR_switches
        self.sched_switches={}
        
    def update_sched(self, tick, switches):
        """Actualiza los datos del scheduler"""
        self.sched_switches[tick] = switches
        
    def update_task(self, name, data):
        """Actualiza los datos de un proceso"""
        # data es del estilo [ticks,prio] o [ticks, tslice] o [ticks,completed])
        try:
            self.tasks[name].append(data)
        except KeyError:
            self.tasks[name] = []
            self.tasks[name].append(data)
        
    def get_task_data(self, name):
        try:
            res = self.tasks[name]
        except KeyError:
            res = None
        return res
    
    def get_sched_data(self):
        # Hay que devolver los datos formateados para el uso en eppli_graph:
        # devolver una lista de listas
        res = [[x,self.sched_switches[x]] for x in self.sched_switches.keys()]
        return res
    
    
if __name__ == "__main__":
    from random import randint
    
    s = sched_stats()
    
    print "Cargando datos de sched:"
    for t in range(0, 20):
        s.update_sched(t, randint(t, t*2))
    print "Datos de sched:"
    print s.get_sched_data()
    
    t_prio = sched_stats()
    print "Cargando datos de prioridades de procesos"
    for t in ["a", "b", "c"]:
        for tick in range(0, 20):
            t_prio.update_task(t, [tick, randint(100, 140)])
    print "Datos de prioridades:"
    for t in ["a", "b", "c"]:
        print "Proceso %s: " % t,
        print t_prio.get_task_data(t)
    
    t_tslice = sched_stats()
    print "Cargando datos de timeslice de procesos"
    for t in ["a", "b", "c"]:
        for tick in range(0, 20):
            t_tslice.update_task(t, [tick, randint(0, 100)])
    print "Datos de timeslices:"
    for t in ["a", "b", "c"]:
        print "Proceso %s: " % t,
        print t_tslice.get_task_data(t)

    t_percent = sched_stats()
    print "Cargando datos de % completado en procesos"
    for t in ["a", "b", "c"]:
        for tick in xrange(20):
            t_percent.update_task(t, [tick, tick*100/20])
    print "Datos de % completado"
    for t in ["a", "b", "c"]:
        print "Proceso %s: " % t,
        print t_percent.get_task_data(t)
    