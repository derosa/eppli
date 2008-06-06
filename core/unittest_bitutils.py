#coding: utf-8
from math import log
from math import floor

def ffs(i):
    """Fórmula mágica para encontrar el primer bit a 1 de un numero.
Se usa esto en lugar de la función ffsl de C por la longitud de los números
de 140 bits que son necesarios en el BITMAP_SIZE."""
#    print " ffs(%d)" % i
    try:
        res = int(round(log(i & (~i+1)) / log(2)))
    except:
        res = -1
    return res
	
def set_bit(i, j):
    """Establecer el bit siempre es posible."""
    res = i ^ (1<<j)
        
    return res

def clear_bit(i, j):
    """Si el bit está establecido, se limpia. 
Si no, no es necesario y se devuelve tal cual."""	
    if (i&(1<<j)):
        ret = i - (1<<j)
    else:
        ret = i
    return ret

for t in range(150):
	new = set_bit(0, t)
	res = ffs(new)
	print "Esperado: %d, obtenido: %d" % (t, res), 
	if t!=res:
		print "*** Bitmap: %d, Bitmap malo: %d" % (set_bit(0, t), set_bit(0, res))
	else:
		print
