Análisis de scheduler\_tick (sched.c@2412):

- Obtiene:
> - CPU actual.
> - rq en ejecución.
> - tarea actual (current).
- Guarda la "hora" en rq->timestamp\_last\_tick
- Si la tarea actual es la "idle":
> - En UP simplemente vuelve, las funciones llamadas no hacen nada.
> - En SMP:
> > - Se comprueba si hay más procesos en la rq en que se ejecuta idle.
> > - Se rebalancea la carga de las CPU's.

> - Se vuelve, pues no se actualizan las stats del proceso idle.
- Si la tarea ha expirado, pero no sacada de ejecución, se activa el flag de "Se necesita re-planifica" y se salta al final de la función.

- Si la tarea es de tiempo real:
> - Si es RR y y agota tu time\_slice:
> > - Se actualiza su time\_slice.
> > - Se indica que no es su primer time\_slice.
> > - Se activa el flag de necesidad de re-planificar.
> > - Se coloca la tarea al final de la cola.

> - Se va al final de la función.

- Si la tarea agota su time\_slice:
> - Se elimina de la prio\_array active.
> - Se establece el flag de re-planificación.
> - Se recalcula su prioridad efectiva (effective\_prio).
> - Se actuliza su time\_slice.
> - Se indica que no es el primer time\_slice.
> - Si expired\_timestamp es 0, se actualiza con los jiffies del sistema.
> - Si la tarea no es interactiva o hay procesos "ahogándose" en la cola de expirados:
> > - Se pone el proceso en la cola de expirados.
> > - Se actualiza el best\_expired\_prio de la rq.

> - Si la tarea es interactiva y no hay procesos "ahogándose" en expired:
> > - Se vuelve a colocar el proceso en la lista de activos.

- Si la tarea NO agota su time\_slice, se comprueba que el time\_slice que le queda no es demasiado grande. Si lo es, se elimina de la cabeza de la lista de procesos y se coloca al final (RR entre procesos de la misma prioridad).

- Salir:

> - Rebalanceo, pero no es necesario en UP.