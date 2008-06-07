#coding: utf-8
from math import log
from math import floor
from bitutils import *

for t in range(150):
	new = set_bit(0, t)
	res = ffs(new)
	print "Esperado: %d, obtenido: %d" % (t, res), 
	if t!=res:
		print "*** Bitmap: %d, Bitmap malo: %d" % (set_bit(0, t), set_bit(0, res))
	else:
		print
