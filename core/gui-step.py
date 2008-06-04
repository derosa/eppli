#!/usr/bin/python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
from sched import scheduler

def sansacabo(w, x):
	gtk.main_quit()
	return False

def avanza(widget, s, t):
	print "Se avanzan cosas: ", t.get_text()
	vueltas = int(t.get_text())
	while vueltas and len(s.tasks):
		s.do_ticks(1)
		vueltas-=1
		
	print "Cosas avanzadas"
s = scheduler()

h = gtk.HBox()
w = gtk.Window(gtk.WINDOW_TOPLEVEL)
w.set_title("Titulazo")
w.connect("delete_event", sansacabo )

i = gtk.Entry(4)
h.pack_start(i)

b = gtk.Button("Avanzar")
b.connect("clicked", avanza, s, i)
h.pack_start(b)

w.add(h)

w.show_all()


gtk.main()
