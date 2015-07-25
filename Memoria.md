# Introducción #
# **El contenido de la memoria ya no se actualiza aquí, sino en el documento propio de la memoria** #
Esta página contiene la memoria del proyecto, para ser formateada y recauchutada luego en el editor.

La memoria debe contener ~60 páginas, junto con una presentación de unas 20.

La primera entrega de la memoria debe tener un índice detallado y algunos capítulos introductorios.

# Índice #

  1. Introducción.
    1. Presentación del proyecto.
    1. Introducción a la planificación de procesos.
    1. El planificador de procesos de linux.
  1. El proyecto _eppli_.
    1. Requisitos y funcionalidades de _eppli_.
    1. El _scheduler_ de linux aplicado a _eppli_.
  1. Diseño de _eppli_.
    1. Herramientas de construcción.
    1. Estructuras de datos.
    1. Subsistemas.
  1. Implementación.
    1. Núcleo de emulación.
    1. Interfaz gráfica.
  1. Bibliografía.
    1. Libros.
    1. Internet.

# Introducción #

## Presentación del proyecto ##

A pesar de la gran cantidad de documentación existente sobre la teoría de planificadores de procesos en sistemas operativos, no existen apenas aplicaciones prácticas de estos principios más allá de su uso real en SS.OO.

La primera dificultad con que un estudiante se encuentra a la hora de encarar estos algoritmos es la falta de resultados prácticos: Ver cómo se evalúan procesos reales, saber por qué el planificador cambia de tarea, cómo se cambia la prioridad de los procesos, cómo afecta el que un proceso sea CPU intensivo o I/O intensivo, etc. Todo esto no es fácilmente mensurable en un S.O. en ejecución, por lo que se hace necesario un método que no solo sea más interactivo y parejo con la velocidad de proceso de la persona, sino que permita indagar en las interioridades del mismo y modificarlo para ver cómo afectan los cambios a los resultados.

La resolución de estos problemas es el objetivo de mi TFC, que consiste en la programación de un emulador del planificador de procesos del kernel linux. El nombre del proyecto es _EPPLI_ (**_Emulador del Planificador de Procesos de Linux_**), y puede seguirse desde http://code.google.com/p/eppli

## Introducción a la planificación de procesos ##

El principal cometido de un sistema operativo es gestionar los recursos de la máquina donde se ejecuta. Se gestiona la memoria, las peticiones de I/O, los dispositivos... y se gestionan procesos.

Un procesador solo puede ejecutar un proceso cada vez, por lo que la aparente ejecución simultánea de muchos procesos (conocida como multitarea), se trata en realidad de un "truco" conjunto del procesador y el SSOO. En realidad lo que ocurre es que el SSOO alterna la ejecución de los procesos de diferentes formas (según el algoritmo de planificación) dando a cada proceso un corto tiempo de CPU de forma que cree la ilusión de ejecución simultánea para el usuario.

Esta gestión de procesos recibe el nombre de planificación de procesos y es llevada a cabo por el planificador de procesos (_process scheduler_). Esta parte del SSOO se encarga de decidir qué proceso debe ejecutarse en un momento determinado en función del entorno. Ésta tarea no es fácil, pues debe intentar cumplir con varios objetivos, a veces incongruentes entre sí:

  1. El tiempo de CPU debe ser repartido de forma justa entre todos los procesos.
  1. Los procesos interactivos deben seguir siéndolo.
  1. A cada proceso debe permitírsele la ejecución durante un mínimo de tiempo.
  1. Ningún proceso debe estar demasiado tiempo sin usar la CPU (_process starvation_)

Puede verse que, por ejemplo, los puntos 1 y 2 son opuestos. No es posible repartir de forma justa el tiempo de CPU entre todos los procesos si se favorecen los procesos interactivos. Cuando se favorece un tipo de procesos, inevitablemente otros procesos "sufren" las consecuencias.

De la misma forma, los puntos 3 y 4 también caen en la contradicción: Si cada proceso debe ejecutarse un mínimo periodo de tiempo, con suficiente número de procesos en ejecución no será posible impedir que un proceso esté demasiado tiempo sin CPU. Por ejemplo, si en un sistema tenemos 10 procesos en ejecución y se ejecutan cada uno de ellos durante 100ms. secuencialmente, habrá un proceso que no podrá usar la CPU hasta que transcurra 1 segundo.

Teniendo en cuenta lo anterior, un planificador de procesos debe tener claro a qué entorno está orientado, pues no es lo mismo un entorno de computación científica donde los procesos usarían la CPU durante horas continuamente si pudieran, que el equipo de un equipo de producción de video, donde los procesos necesitan capacidad de ejecución y reacción en tiempo real. Es necesario un compromiso entre los procesos interactivos y los que usan intensivamente la CPU.

Históricamente se han diseñado los planificadores de procesos siguiente esquemas simples, pero el cambio de las necesidades de los usuarios, normalmente orientados a aplicaciones más interactivas) han hecho necesaria la evolución de estos esquemas. Algunos de estos métodos simples son:

  * FIFO (_First In, First Out_): Consiste en despachar los procesos por orden de llegada y hasta que estos abandonen voluntariamente la CPU. Su uso es más obvio en los primeros sistemas por lotes, en los que no existía interactividad del usuario.
  * Por rotación (_Round Robin_): Los procesos se ejecutan durante un cuanto de tiempo determinado. Cuando este cuanto expira se pasa directamente al siguiente proceso de la lista, volviendo al primero cuando se termina con el último proceso.
  * Colas multinivel (_Multilevel queues_): Diversas colas administradas por _Round Robin_, cada una de una prioridad. Los procesos pueden pasar de una cola a otra, dependiendo de ciertos factores.
  * Planificador por lotería (_Lottery Scheduling_): Consiste en asignar a cada proceso un número de ticket. Cuando hay que seleccionar un proceso, el planificador selecciona un número al azar y ejecuta el proceso correspondiente.

Otro concepto necesario para comprender la extensión de la problemática asociada a la planificación de procesos es el de apropiación (_preemption_):
La apropiación consiste en arrebatar la CPU a un proceso en ejecución mientras aún no la ha cedido voluntariamente. Sistemas operativos monotarea y monousuario, como MS-DOS, carecen del concepto de apropiación, por lo que un proceso continuaba la ejecución hasta que terminaba o cedía voluntariamente la CPU (_cooperative multitasking_). Esto tiene la ventaja de ser un sistema fácil de desarrollar y mantener, pues simplemente se ejecuta la aplicación solicitada, pero implica que el sistema queda a merced del proceso en ejecución. Actualmente la mayoría de SSOO hacen uso de la apropiación, que hace posible retirar la CPU a un proceso cuando se determina que su cuota de tiempo ha finalizado. En el kernel linux es posible incluso apropiarse de la CPU mientras el proceso ejecuta código del kernel. Por ejemplo, puede quitarse la CPU a un proceso mientras está llamando a la función sys\_read del sistema.

## El planificador de procesos de linux ##

El planificador de procesos de linux es una de las partes que más reformas sufre a lo largo de las diferentes versiones del núcleo. Empezando por la serie 2.4, en la que el planificador constaba de unas 1.400 líneas de código, hasta la serie 2.6, con más de 5.000 (2.6.11) u 11.000 (2.6.25-rc8). Esta evolución es la responsable de la calidad del planificador, que ha pasado de ser de una eficiencia linear (O(n), serie 2.4) a constante (O(1), serie 2.6).

La principal debilidad del planificador de la serie 2.4 es el algoritmo para determinar la cantidad de tiempo que un proceso podía ejecutarse, que se calculaba iterando sobre toda la lista de procesos. Además, el tiempo medio asignado a los procesos es de 210ms, que contrasta con la media de 100ms de la serie 2.6. Recordemos que con estas cantidades, un servidor con 100 procesos usando todo el tiempo asignado puede hacer esperar hasta 20 segundos al proceso de más baja prioridad del sistema, lo que no es admisible.

El objetivo del planificador en la serie 2.6 es mejorar los puntos débiles de la serie 2.4. Esto se consigue con el que se conoce como "The O(1) Scheduler", o planificador de tiempo constante, que tiene siempre el mismo coste de ejecución, independientemente del número de procesos del sistema.

Se presentan a continuación las estructuras de datos y algoritmos que componen el planificador de procesos de linux 2.6.11.

### Estructuras de datos ###

#### **_prio\_array_** ####

Estructura de procesos y sus prioridades:
Miembros de la estructura:

  * **_nr\_active_**: Número de procesos activos.
  * **_bitmap`[BITMAP_SIZE]`_**: Mapa de bits indicando para qué prioridades hay procesos en la lista.
  * **_queue`[MAX_PRIO]`_**: Array de listas.

MAX\_PRIO es 140 y BITMAP\_SIZE depende de la arquitectura, pues se calcula como:

> `#define BITMAP_SIZE ((((MAX_PRIO+1+7)/8)+sizeof(long)-1)/sizeof(long))`

Por lo que en máquinas de 32 bits será 5 unsigned long y en máquinas de 64, 3 unsigned long.

#### **_runqueue_** ####

Contiene dos arrays de prioridades (_prio\_array_): de procesos activos y expirados.
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

#### **task\_struct** ####

Esta estructura es la utilizada por el kernel para el control de los procesos. Dado que todos los campos no son necesarios para la planificación, solo se presentan aquellos que son usados.

Campos de _task\_struct_ a tener en cuenta durante la planificación:

  * **flags**: Contiene una bandera (_flag_) que indica si el planificador debe ser invocado.
  * **state**: Estado del proceso (TASK\_RUNNING, TASK\_UNINTERRUPTIBLE...)
  * **prio**: Prioridad dinámica.
  * **run\_list**: Enlaza con el siguiente y anterior proceso de la _rq_ a la que pertenece.
  * **array**: Apunta al _prio\_array_ al que pertenece el proceso.
  * **sleep\_avg**: Tiempo medio durmiendo.
  * **timestamp**: Marca de tiempo del momento de inserción del proceso en la _rq_, o tiempo del último cambio de proceso que incluyó al proceso.
  * **last\_ran**: Tiempo del último cambio de proceso que reemplazó al proceso.
  * **activated**: Marca cuando el proceso es "levantado".
  * **policy**: Tipo de planificación del proceso (_SCHED\_NORMAL, SCHED\_RR o SCHED\_FIFO_).
  * **time\_slice** : Ticks que le quedan al proceso de su cuanto.
  * **first\_time\_slice**: Vale 1 si el proceso nunca ha agotado su cuanto de tiempo.
  * **rt\_priority**: Prioridad de tiempo real del proceso.

### Funcionamiento ###

La relación entre estas estructuras de datos es muy sencilla, y se explicará a continuación:

  * **IMAGEN esquema estructuras planificador.png IMAGEN**

Por cada CPU o núcleo del sistema, el kernel mantiene una estructura denominada "_runqueue_". Esta estructura contiene la información  sobre el número de procesos en ejecución, la carga de la CPU, "fecha" del último _tick_ del reloj, etc. Los dos miembros más importantes de la _runqueue_ son dos punteros a sendas estructuras del tipo _prio\_array_ (array de prioridades). El _prio\_array_ es la pieza fundamental en la que está basado este planificador de la serie 2.6 y el responsable de que opere en tiempo constante O(1).

El propósito del _prio\_array active_ y el _prio\_array expired_ se explica con el funcionamiento a grandes rasgos del planificador:

  * Cada vez que una tarea se incorpora al sistema, el planificador la inserta en el _prio\_array active_, pues se trata de una tarea activa:
    * Siendo la prioridad del proceso N, se activa el bit N de _bitmap_ para informar de que hay una tarea de esa prioridad disponible en la cola.
    * Se inserta la tarea en la lista correspondiente a su prioridad, utilizando la misma como índice (_queue[N](N.md)_).
  * Con cada tick de reloj, el planificador puede comprobar mediante una sencilla instrucción cuál es el primer bit activo (a 1) de _bitmap_.
  * Sabiendo cuál es el primer bit activo, se usa ese valor como índice en la lista _queue_ para localizar el proceso a ejecutar.
  * Los procesos se ejecutan hasta que termina su cuanto de tiempo, duermen, o una tarea de mayor prioridad lo reemplaza.
  * Una vez que el proceso ha consumido su cuanto de tiempo:
    * Se elimina del _prio\_array active_
    * Si es el último proceso de su prioridad (_queue[N](N.md)_ será NULL), se pone a 0 el bit correspondiente a su prioridad en _bitmap_.
    * El planificador calcula una nueva prioridad para el proceso, teniendo el cuenta el tiempo que ha dormido, cuán interactivo es, etc.
    * El proceso se pasa al _prio\_array expired_, activando a su vez el bit de su prioridad del miembro _bitmap_ de _expired_.
  * Eventualmente, el _prio\_array active_ quedará sin procesos (nr\_active = 0), por lo que el planificador intercambia los punteros _active_

&lt;-&gt;

 expired_._

Este último paso, el intercambio de los punteros a los _prio\_array active_ y _expired_ es el que evita que tengan que pasarse todos los procesos "caducados" de un array a otro, por lo que se evita una costosa operación O(n). La otra operación que hace de éste un planificador de coste O(1) es la selección del proceso a ejecutar, pues es tan simple como averiguar el primer bit activo del _bitmap_ y seleccionar el primer proceso de la lista correspondiente a la posición de ese bit. Así se consigue evitar el pesado bucle que recorría todos los procesos en busca del de mayor prioridad en el planificador de la serie 2.4.



A partir de la versión 2.6.23, linux usa un planificador conocido como CFS (_Completely Fair Scheduler_), que en lugar de colas de ejecución (_run queues_), usa una estructura de datos llamada "árbol Rojo-Negro" (_Red-Black Tree_).