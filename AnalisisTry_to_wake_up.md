Análisis de try\_to\_wake\_up (sched.c@985):

/**> 972** try\_to\_wake\_up - wake up a thread
> 973 **@p: the to-be-woken-up thread
> 974** @state: the mask of task states that can be woken
> 975 **@sync: do a synchronous wakeup?
> 976**
> 977 **Put it on the run-queue if it's not already there. The "current"
> 978** thread is always on the run-queue (except when the actual
> 979 **re-schedule is in progress), and as such you're allowed to do
> 980** the simpler "current->state = TASK\_RUNNING" to mark yourself
> 981 **runnable without the overhead of this.
> 982**
> 983 **returns failure only if the task is already active.
> 984**/

- Se adquiere el bloqueo de la última rq (CPU) que ejecutó el proceso. Como
> nos ceñimos a sistemas UP no es necesario pues siempre será la misma rq.
- Si la máscara de procesos a despertar no coincide con el estado del proceso,
> se salta a "out".
- Si el proceso ya pertenece a una rq se sale, pues el proceso ya está corriendo.
- Tocho para SMP que podemos ignorar.
- Se decrementa el campo rq-> uninterruptible si el proceso estaba en ese estado,
> además su campo "activated" se pone a -1, que será usado en "recalc\_task\_prio"
- Se llama a activate\_task (sched.c@XXX):
> - Obtiene el timestamp.
> - Invoca a recalc\_task\_prio()
> - Establece el campo "activated" de la tarea en función de su estado anterior
> > y el motivo del "despertar".

> - Actualiza el timestamp del proceso según el valor obtenido en el primer paso
> - Inserta el proceso en la prio\_array active de la rq e incrementa el número
> > de procesos en ejecución de la mism.
- Si la CPU "objetivo" no es la actual o el flag sync es 1, se comprueba si el

> proceso tiene mayor prioridad que el que está actualmente en ejecución (current).
> - Si es así, se ejecuta resched\_task para sustituir al proceso actual.
> - En UP, simplemente se establece el flag de replanificación.
- Se establece el estado de la tarea como "en ejecución".
- Se sale con 1 si el proceso se "despertó" o 0 si no lo hizo.