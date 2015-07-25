Análisis de la función schedule (sched.c@2662):

> - Se comprueba si estamos en medio de una operación atómica y vuelca la pila
> si es así (para depurar),excepto si el proceso está en estado de terminación.
need\_resched:
> - Se desabilita la apropiación.
> - El proceso anterior es el actual (prev = current)
need\_resched\_nonpreemtible:
> - Obtiene la rq.
> - Si el proceso actual era "idle" y además no estaba en ejecución, vuelca la
> pila.
> - "now" = reloj
> - run\_time = min(now - prev->timestamp, NS\_MAX\_SLEEP\_AVG)
> - Se ajusta el run\_time según un bonus.
> - Con el flag PF\_DEAD, el proceso entra en estado EXIT\_DEAD
> - Si el proceso previo era INTERRUPTIBLE y tiene señales pendientes, se cambia su estado a RUNNING. Si era UNINTERRUPTIBLE, se desactiva la tarea.
> > - Si la cpu no tiene procesos en estado running, se intenta balancear las cpus y se comprueba de nuevo. si sigue siendo así, se cambia a la tarea idle de la cpu, se resetea el expired timestamp y se intenta despertar procesos durmientes. En UP esta llamada no hace nada, en SMP busca procesos factibles de ser despertados, por lo que se vuelve a comprobar a comprobar si hay tareas que puedan ejecutarse. De ser así se vuelve a switch\_tasks:.
> > - En otro caso (la cpu tiene procesos "runnables"), se comprueban los procesos dependientes, que de nuevo en UP devolverá 0.
> > > - Si no hay procesos runnables, se salta a go\_idle para conmutar al proceso idle de la cpu.

> > - Si el prio\_array active no tiene procesos activos, se intercambia con expired y se resetea el expired\_timestamp de la rq y se pone la best\_expired\_prio a MAX\_PRIO.
> > - Si hay procesos activos se incrementa la estadística de número de cambios de contexto.
> > - Se busca el primer bit activado del bitmap.
> > - Se obtiene la cola correspondiente a ese bit y se obtiene la siguiente tarea de la lista (en RR): "next"
@2783:
> > - Si la tarea "next" no es de tiempo real y se ha levantado de un estado durmiente, se recalcula su prioridad al añadirse el tiempo que el proceso ha estado esperando en la runqueue. Si el proceso estaba en el estado 2, (es decir, levantado por una interrupción o función aplazada, se le añade todo el tiempo de espera completo. Esto es así porque las tareas interactivas son más propensas a ser levantadas por eventos asíncronos (como la pulsación de una tecla y su consiguiente llamada de interrupción). En caso de estado 1 (activated == 1), solo se añade una porción del tiempo de espera en la runqueue. A continuación se elimina la tarea del prio\_array en el que estaba, se recalcula su prioridad (recalc\_task\_prio) y se vuelve a insertar en la prio\_array.
> > - next->activated = 0
switch\_task:

> - Se elimina el flag de replanificación de "prev".
> - Se resta el tiempo de ejecución del tiempo medio durmiendo de prev:
> > prev->sleep\_avg = min(prev->sleep\_avg - run\_time, 0)

> - Se iguala el timestamp y el last\_ran de "prev" con "now".
> - Existe la posibilidades de que next y prev sean el mismo proceso al no haber ninguno de mayor o igual prioridad que lo sustituya. En ese caso se salta el proceso de cambio de contexto.
> - Pero si no son el mismo proceso, se procede al cambio de proceso:
> > - next->timestamp = now
> > - Cambios de contexto de la rq++
> > - Proceso current = next
> > - La función "context\_switch" se encarga de establecer correctamente el espacio de direcciones de "next" en función del tipo de proceso que sea. No nos interesa a efectos de la emulación.

> - Si ningún otro proceso ha establecido el flag de replanificación, termina la función.