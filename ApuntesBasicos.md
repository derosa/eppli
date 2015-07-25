# Introducción #

Conceptos de planificadores de procesos, en especial del kernel linux.


## Tipos de procesos ##

  1. CPU _bound_: Son procesos que pasan la mayor parte del tiempo consumiendo CPU. Por ejemplo compiladores, aplicaciones de cálculo intensivo o motores de búsqueda.
  1. I/O _bound_: Son procesos que pasan la mayor parte del tiempo bloqueados esperando un evento de entrada o salida. Por ejemplo un procesador de textos, una aplicación gráfica (calculadora p.ej.) o una consola.
  1. Tiempo real (_RT_): Con requerimientos de planificación muy estrictos y un tiempo de respuesta con una muy pequeña variación. Por ejemplo aplicaciones de sonido o de reproducción de vídeo.

La clasificación de los procesos se lleva a cabo mediante algoritmos heurísticos que determinan si un proceso es "I/O _bound_ o CPU _bound_".

## Reemplazo de procesos (_Process preemption_) ##

Los procesos en Linux son "reemplazables" (_preemptable_). Esto significa que cuando un proceso pasa a estado de ejecución, el kernel comprueba si su prioridad es mayor que el proceso ejecutándose actualmente (_current_). Si lo es, detiene la ejecución de _current_, pone el nuevo proceso en la cola de ejecución y llama al planificador para que seleccione un nuevo proceso (que seguramente será el nuevo). El proceso reemplazado no se suspende ni cambia de estado, sino que continúa en el estado _TASK\_RUNNING_.

## Duración del quanto (_quantum_) ##

La duración del quanto no debe ser ni muy pequeña ni muy grande.

Si fuese demasiado corto, p. ej. 5 ms., y el sistema tardara 5 ms. en efectuar un cambio de contexto, el 50% del tiempo de CPU se pasaría haciendo cambios de contexto.
En cambio, con un quanto demasiado largao, p.ej. 1 segundo, las aplicaciones se ejecutarían durante ese tiempo y tardarían en ejecutarse de nuevo 1 segundo x N procesos. Si en un sistema hubieran 50 procesos, tardaría 50 segundos en recuperar la CPU para seguir ejecutándose. Esto haría que los procesos interactivos fueran no interactivos :).

En linux se adopta el compromiso de hacer el quanto tan largo como sea posible, manteniendo un buen tiempo de respuesta.

## El algoritmo de planificación (_scheduling algorith_) ##

Los planificadores de versiones anteriores de linux eran del orden O(n), pues en cada cambio de contexto, el kernel recorría la lista de procesos eligiendo el más adecuado para ejecutarse.

El algoritmo de la serie 2.6 es más sofisticado, pues :
  * Elige el proceso a ejecutar en tiempo constante O(1)
  * Cada CPU tiene su propia cola de procesos ejecutables, lo cual hace que escale muy bien.
  * El nuevo algoritmo distingue los procesos interactivos mejor.

Hay tres clases de planificación:
  * SCHED\_FIFO: Una FIFO de procesos de tiempo real. Cuando un proceso entra en ejecución, tiene la CPU hasta que decida dejarla. Solo un proceso de más prioridad puede arrebatarle la CPU.
  * SCHED\_RR: Procesos en _Round Robin_. Cuando se le asigna la CPU a un proceso, éste se pasa al final de la cola de ejecución.
  * SCHED\_NORMAL: Procesos de tiempo compartido.

## Planificación de procesos convencionales (SCHED\_NORMAL) ##

Cada proceso tiene una prioridad estática que abarca de 100 (la más alta) a 139 (la más baja). La prioridad por defecto es 120.
Los procesos hijos heredan la prioridad estática del padre.

### Quanto base ###

El quanto se calcula (pag. 263):
> quanto base = (140 - static\_prio) x N ; N=static\_prio<120?20:5

### Prioridad dinámica y tiempo medio durmiendo ###

La prioridad dinámica abarca de 100 (la más alta) a 139 (la más baja). Este es el valor que el planificador mira realmente cuando elige qué proceso debe ejecutarse a continuación.
Se relaciona con la prioridad estática por la siguiente fórmula:
> dyn\_prio = max (100, min(static\_prio - bonus + 5, 129) )
_bonus_ abarca de 0 a 10. Un valor menor que 5 penaliza y un valor mayor a 5 recompensa al proceso, elevando su prioridad dinámica.

El valor de _bonus_ depende del pasado del proceso, de cuánto tiempo haya pasado durmiendo.

El tiempo medio durmiendo (_average sleep time_) es la media de nanosegundos que el proceso ha estado durmiendo. Diferentes estados cuentan de diferente forma a la hora de calcular este valor (TASK\_INTERRUPTIBLE != TASK\_UNINTERRUPTIBLE). Este tiempo también decrece cuando el proceso está en ejecución y además nunca puede pasar de 1 segundo.

Valores de _bonus_ en p. 264.

Un proceso se considera interactivo si:
> dyn\_prio <= 3 x static\_prio / 4 + 28

> ó

> bonus - 5 >= static\_prio / 4 + 28

static\_prio /4 + 28 se conoce como "delta interactivo"

### Procesos activos y expirados ###

cuando un proceso agota su tiempo, puede ser sustituido por otro de menor prioridad que no haya consumido todo su tiempo.

Se mantienen dos juegos de procesos:
  * Activos: Estos procesos no han consumido su quanto de tiempo y se les permite correr.
  * Expirados: Han consumiso su quanto de tiepo y no pueden ejecutarse hasta que todos los procesos activos terminen.

El kernel intenta favorecer a los procesos interactivos. Un proceso no interactivo que acabe su quanto de tiempo para a la lista de procesos expirados, pero si un proceso es interactivo y acaba su tiempo es reinsertado en la lista de procesos activos y se le "rellena" su tiempo, para ser ejecutado de nuevo cuando llegue su turno.

De todas formas, el kernel manda un proceso interactivo a la cola de expirados si el proceso expirado más antiguo ha esperado durante mucho tiempo o si un proceso expirado tiene mayor prioridad estática (menor valor) que el proceso interactivo. De esta forma en algún momento la lista de procesos activos se vaciará y la de procesos expirados podrá ejecutarse.

## Planificación de procesos de tiempo real ##

Cada proceso tiene una prioridad de tiempo real (a partir de ahora, rt\_prio) que varía de 1 (la más alta) a 99 (la más baja).
Se favorece el proceso de prioridad alta sobre el de baja mientras se mantenga ejevutable (_runnable_).
Estos procesos son siempre activos (no expiran).
El usuario puede cambiar la rt\_prio de estos procesos mediante syscalls.
Un proceso de RT solo es reemplazado por otro si:
  * Es reemplazado (_preempted_) por otro de mayor rt\_prio.
  * El proceso bloquea/duerme.
  * El proceso se para o muere.
  * Libera voluntariamente la CPU.
  * Es un proceso SCHED\_RR y agota su quanto de tiempo.

Las llamadas nice() y setpriority() no alteran la _rt\_prio_ de un proceso RR, sino que alteran la duración del quanto base.