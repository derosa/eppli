# Introducción #
Este documento presenta las estructuras de datos del planificador de procesos.
Las estructuras que no sean relevantes para el emulador (SMT/SMP, estadísticas, etc.) serán omitidas.

## _prio\_array_ ##

Estructura de procesos y sus prioridades:
Miembros de la estructura:

  * **_nr\_active_**: Número de procesos activos.
  * **_bitmap`[BITMAP_SIZE]`_**: Mapa de bits indicando para qué prioridades hay procesos en la lista.
  * **_queue`[MAX_PRIO]`_**: Array de listas.

MAX\_PRIO es 140 y BITMAP\_SIZE depende de la arquitectura, pues se calcula como:

> `#define BITMAP_SIZE ((((MAX_PRIO+1+7)/8)+sizeof(long)-1)/sizeof(long))`

Por lo que en máquinas de 32 bits será 5 unsigned long y en máquinas de 64, 3 unsigned long.

Cada vez que una tarea de prioridad N se introduce en esta estructura, se activa el bit N del _bitmap_ y se encola el proceso en _`queue[N]`_.

Saber qué proceso debe ejecutarse a continuación es tan simple como averiguar el primer bit activo del _bitmap_ y seleccionar el primer proceso de la lista correspondiente a la posición de ese bit.

## _runqueue_ ##

Hay una _runqueue_ (en adelante _rq_) por procesador.
Contiene dos arrays de prioridades (_prio\_array_): de procesos activos y expirados. Cuando la activa se vacía, se intercambia con la de expirados.
Miembros de la estructura:

  * **_lock_**: Bloqueo para que solo un proceso pueda modificar la _rq_ en un momento dado.
  * **_nr\_running_**: Número de procesos ejecutables en la cola.
  * **_cpu\_load_**: Carga de la CPU.
  * **_nr\_switches_**: Número de cambios de contexto. Solo se usa a efectos estadísticos.
  * **_expired\_timestamp_**: tiempo transcurrido desde el último intercambio de los _prio\_array_ active 

&lt;-&gt;

expired.
  * **_nr\_uninterruptible_**: Tareas en estado TASK\_UNINTERRUPTIBLE.
  * **_timestamp\_last\_tick_**: Tiempo del último _scheduler tick_. Se usa para saber si una tarea debería considerarse _cache hot_ (con posibilidades de tener aún datos en la caché de la CPU).
  * **_curr_**: Puntero al proceso actual _current_.
  * **_idle_**: Puntero a la tarea que se ejecuta cuando no hay nada que ejecutar.
  * **_active_**: Puntero a _prio\_array_  de tareas activas (con tiempo en sus _timeslices_).
  * **_expired_**: Puntero a _prio\_array_ de tareas que han agotado sus ranuras de tiempo de ejecución.
  * **_arrays`[2]`_**: El array real de _prio\_array_.
  * **_best\_expired\_prio_**: La mayor prioridad de las tareas expiradas.
  * **_nr\_iowait_**: Tareas esperando un evento de I/O.