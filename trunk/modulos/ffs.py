#!/usr/bin/python

from math import log

def ffs(t):
	try:
		res=int(log(t & (~t+1) )/log(2))
	except OverflowError:
		res=-1

	return res
	
def set_bit(t, b):
	return t + pow(2,b)
	
def clear_bit(t, b):
	return t - pow(2,b)

if __name__ == "__main__":
	from sys import argv
	if len(argv) != 2:
		print "Uso: %s numero" % argv[0]
	else:
		print ffs(long(argv[1]))
