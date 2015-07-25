# Introducción #

Se trata de un emulador de uno o varios planificadores de tareas del kernel linux.

El emulador debe reflejar paso a paso qué ocurre: Actualización de la prioridad de las tareas, selección de siguiente tarea a ejecutar, cálculo de timeslices, etc.


# Detalles #

  * Varias tareas ejecutándose.
  * Cada tarea tiene un comportamiento predefinido. Por ejemplo, 10ms de _CPU-bound_, 5 durmiendo y 20 de _IO-bound_.
  * En cada momento se visualiza el estado de las tareas.
  * Debe poder añadirse una tarea en cualquier momento de la ejecución (_spawn new process_).
  * La aplicación avanzará por "_ticks_" (equivalentes a interrupciones del reloj) o continuamente.
  * La interfaz estará separada de la lógica del _scheduler_ para poder simular varios distintos.
  * En cualquier momento el simulador puede pasar del estado _paused_ a _running_.
  * El programa simulará lo más fidedignamente posible las estructuras de datos internas del _scheduler_ real.
  * **Opcionalmente** se simularán los planificadores para varios núcleos (_SMP_)