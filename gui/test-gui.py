#!/usr/bin/python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

def botonSalir_clicked(widget):
	print "Se pulso el boton que dice.. ", widget.get_label()
	
eventos = { "on_botonSalir_clicked": botonSalir_clicked,
"on_mainWindow_destroy": gtk.main_quit}

appXML = gtk.glade.XML("eppli-test1.glade")
appXML.signal_autoconnect(eventos)

mainWindow = appXML.get_widget("mainWindow")
toolbar = appXML.get_widget("toolbar")
# Ver http://library.gnome.org/devel/gtk/2.11/gtk-Stock-Items.html
# para los iconitos stock :)

boton_play = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
boton_play.set_label("Iniciar")
boton_play.connect("clicked", botonSalir_clicked)

boton_pause = gtk.ToolButton(gtk.STOCK_MEDIA_PAUSE)
boton_pause.set_label("Pausar")
boton_pause.connect("clicked", botonSalir_clicked)

boton_new = gtk.ToolButton(gtk.STOCK_ADD)
boton_new.set_label("Nuevo proceso")
boton_new.connect("clicked", botonSalir_clicked)

toolbar.add(boton_play)
toolbar.add(boton_pause)
toolbar.add(boton_new)


#mainWindow.connect("destroy", gtk.main_quit)	
mainWindow.show_all()

res = mainWindow.show()

gtk.main()

print "Salida:", res
