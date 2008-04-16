#!/usr/bin/python

from math import log

# Fórmula mágica para encontrar el primer bit a 1 de un numero.
# Se usa esto en lugar de la función ffsl de C por la longitud de los números
# de 140 bits que son necesarios en el BITMAP_SIZE

def ffs(t):
	try:
		res=int(log(t & (~t+1) )/log(2))
	except OverflowError:
		res=-1
	return res
	
# Establecer el bit siempre es posible.
def set_bit(t, b):
	return t + (1<<b)
	
# Si el bit está establecido, se limpia. Si no, no es necesario y se devuelve tal cual.
def clear_bit(t, b):
	if (t&(1<<b)):
		ret= t - (1<<b)
	else:
		ret = t
	return ret

if __name__ == "__main__":
	from sys import argv
	if len(argv) != 2:
		print "Uso: %s numero" % argv[0]
	else:
		print ffs(long(argv[1]))
