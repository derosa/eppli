#!/usr/bin/python
# coding: utf-8
"""Utilidades para manipulación de bits en enteros."""

from math import log

def ffs(i):
    """Fórmula mágica para encontrar el primer bit a 1 de un numero.
Se usa esto en lugar de la función ffsl de C por la longitud de los números
de 140 bits que son necesarios en el BITMAP_SIZE."""

    try:
        res = int(log(i & (~i+1)) / log(2))
    except OverflowError:
        res = -1
    return res
	
def set_bit(i, j):
    """Establecer el bit siempre es posible."""
    return i + (1<<j)

def clear_bit(i, j):
    """Si el bit está establecido, se limpia. 
Si no, no es necesario y se devuelve tal cual."""	
    if (i&(1<<j)):
        ret = i - (1<<j)
    else:
        ret = i
    return ret

if __name__ == "__main__":
    from sys import argv
    if len(argv) != 2:
        print "Uso: %s numero" % argv[0]
    else:
        print ffs(long(argv[1]))
