Se inicia el programa:

**Crea Scheduler:
> - scheduler crea cpu.
> - cpu crea runqueue
> - runqueue crea 2 prio\_array.** Se llama a scheduler.add\_dir\_tasks(directorio):
> - Por cada fichero en el dir
> > - Crea una nueva task(file) y llama a do\_fork(task)
> > > - Inicializa los valores iniciales de la tarea
> > > - Inserta el proceso en la lista global de procesos.
> > > - Llama a task.activate() si su estado es RUNNING

**Se llama a run():**

while 1:
  * comprueba flags de ejecución:

> > si normal\_run = False:
> > > - avanzar solo un tick: N = ticks
> > > - pausar: N = 1
        * Si no normal\_run && N != 0:
    * do\_tick(N):
> > > - Mientras N--:
      * check\_tasks():
> > > > - Por cada tarea durmiente, comprueba si su nuevo estado según la línea
> > > > temporal es != durmiente. Si es así se llama a try\_to\_wake\_up. (Con esto
> > > > se emula una waitqueue).
> > > > - Comprueba si current ha cambiado de estado a durmiente. Si es así,
> > > > se llama echa a dormir (cambiando el estado) y se activa NEED\_RESCHED.
      * scheduler\_tick()
    * Si NEED\_RESCHED o !(tick%HZ):
      * schedule()
    * do\_tick():

> > > - cpu.advance\_tick()
> > > - current.localtime++
> > > - para cada tarea durmiendo:
> > > > tarea.localtime++
    * sleep(1/HZ)
  * Si normal\_run = False, avanzar solo N ticks: N--