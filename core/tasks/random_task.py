#!/usr/bin/python
#coding=utf-8

from random import randrange

### Genera tareas aleatoriamente

state = {0: "INTERRUPTIBLE", 1: "UNINTERRUPTIBLE", 2: "RUNNING", 3: "EXIT"}
salida={}

for t in range(1, 100):
	when = randrange(1, 10)*t
	what = state[randrange(3)]
	salida[when] = what
	

valores = salida.keys()
valores.sort()

print "NAME=XXX"
print "CLASS=NORMAL"
print "PRIO=120"

for v in valores:
	print "%s=%s" % (v,salida[v])
	
print "1000=RUNNING"
print "1001=EXIT"
