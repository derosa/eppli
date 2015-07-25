# Avanzadilla de las clases, métodos y módulos. #

  * clase scheduler:
    * tiene una CPU (potencialmente podría ser cpus=()) sobre la que se ejecuta.
    * métodos para avanzar el tiempo (scheduler\_tick(times=1))
    * avanza N unidades de tiempo (scheduler\_tick(N) )
    * métodos de acceso rápido a toda info (rq, prio\_arrays, tasks...)
    * Gestiona las tareas (añade, elimina)
    * El estado de las tareas se comprueba y cambia en scheduler\_tick llamando a "advance\_tasks" o similar.
    * Tiene las variables de "tuneo" (HZ, MAX\_PRIO, etc).
    * Tiene el método "scheduler" con toda la pesca.

  * clase cpu:
    * tiene una runqueue
    * mantiene la "hora" del sistema (equivale al tsc).

  * clase runqueue:
    * tiene 2 prio\_array.
    * Métodos para actuar sobre la runqueue

  * clase prio\_array:
    * estructura prio\_array
    * métodos para modificarlo.

  * clase task:
    * Contiene info del proceso.
    * Tiene "timeline" de estados (running, io wait)
    * La timeline es relativa a la hora local de la cpu, no absoluta.
    * De esta forma, pueden "aprovecharse" procesos repitiéndolos en varios momentos.

  * módulo epplimodule:
    * Módulo en C
    * Acceso a funciones no posibles en python
    * p.ej rdtsd

  * módulo bitutils:
    * Funciones para manipulación de bits (ffs, set & clear bit).


