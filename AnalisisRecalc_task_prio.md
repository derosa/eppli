Análisis de recalc\_task\_prio (sched.c@649)

  * Se calcula sleep\_time = min( now - p->timestamp, NS\_MAX\_SLEEP\_AVG)
  * Si es mayor que 0:
    * Si no es tarea del kernel, su estado era "-1" (levantado desde uninterruptible) y llevan durmiendo más que cierto límite:
      * Se establece el campo de tiempo  medio durmiendo a un valor de 900 ticks (obtenido empíricamente).
    * Else:
      * Se recalcula el sleep\_time a partir del CURRENT\_BONUS del proceso actual.
      * Si la tarea no es del kernel y se levanta de UNINTERRUPTIBLE:
        * Si su tiempo medio durmiendo es superior a lo que le correspondería, se pone a 0.
        * Si no, si la suma del tiempo durmiendo y la media es superior al límite que le corresponde, se establece el tiempo medio a lo que corresponde al y el tiempo durmiendo se pone a 0.
      * Se suma el tiempo durmiendo a la media.
      * La media durmiendo = max (tiempo durmiendo, tiempo máximo durmiendo media)

  * Se calcula la prioridad efectiva (effective\_prio). Est prioridad de forma rápida es:
`	din_prio = max (100, min (static_prio - bonus + 5, 139) )`
