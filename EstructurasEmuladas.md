# Introducción #

Estructuras de datos que serán emuladas. Pueden coincidir total o parcialmente con las que aparecen en [EstructurasDeDatos](EstructurasDeDatos.md)

# Estructuras #

## Proceso ##
Contiene los campos de la estructura _task\_struct_ utilizados por el planificador. Muchos de sus campos se expondrán en el emulador.

Campos:
  * **flags**: Contiene un _flag_ que indica si el planificador debe ser invocado.
  * **state**: Estado del proceso (TASK\_RUNNING, TASK\_UNINTERRUPTIBLE...)
  * **prio**: Prioridad dinámica.
  * **run\_list**: Enlaza con el siguiente y anterior proceso de la _rq_ a la que pertenece.
  * **array**: Apunta al _prio\_array_ al que pertenece el proceso.
  * **sleep\_avg**: Tiempo medio durmiendo.
  * **timestamp**: Marca de tiempo del momento de inserción del proceso en la _rq_, o tiempo del último cambio de proceso que incluyó al proceso.
  * **last\_ran**: Tiempo del último cambio de proceso que reemplazó al proceso.
  * **activated**: Marca cuando el proceso es "levantado".
  * **policy**: Tipo de planificación del proceso (_SCHED\_NORMAL, SCHED\_RR o SCHED\_FIFO_).
  * **time\_slice** : Ticks que le quedan al proceso de su quanto.
  * **first\_time\_slice**: Vale 1 si el proceso nunca ha agotado su quanto de tiempo.
  * **rt\_priority**: Prioridad de tiempo real del proceso.

## prio\_array ##

Tal como está redactada en [EstructurasDeDatos](EstructurasDeDatos.md).

Miembros de la estructura:

  * **nr\_active**: Número de procesos activos.
  * **bitmap`[BITMAP_SIZE]`**: Mapa de bits indicando para qué prioridades hay procesos en la lista.
  * **queue`[MAX_PRIO]`**: Array de listas.

## _runqueue_ ##

Tal como está redactada en [EstructurasDeDatos](EstructurasDeDatos.md).

Miembros de la estructura:

  * **lock**: Bloqueo para que solo un proceso pueda modificar la _rq_ en un momento dado.
  * **nr\_running**: Número de procesos ejecutables en la cola.
  * **cpu\_load**: Carga de la CPU.
  * **nr\_switches**: Número de cambios de contexto. Solo se usa a efectos estadísticos.
  * **expired\_timestamp**: tiempo transcurrido desde el último intercambio de los _prio\_array_ active 

&lt;-&gt;

expired.
  * **nr\_uninterruptible**: Tareas en estado TASK\_UNINTERRUPTIBLE.
  * **timestamp\_last\_tick**: Tiempo del último _scheduler tick_. Se usa para saber si una tarea debería considerarse _cache hot_ (con posibilidades de tener aún datos en la caché de la CPU).
  * **curr**: Puntero al proceso actual _current_.
  * **idle**: Puntero a la tarea que se ejecuta cuando no hay nada que ejecutar.
  * **active**: Puntero a _prio\_array_  de tareas activas (con tiempo en sus _timeslices_).
  * **expired**: Puntero a _prio\_array_ de tareas que han agotado sus ranuras de tiempo de ejecución.
  * **arrays`[2]`**: El array real de _prio\_array_.
  * **best\_expired\_prio**: La mayor prioridad de las tareas expiradas.
  * **nr\_iowait**: Tareas esperando un evento de I/O.