#!/usr/bin/python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

from random import sample

def crear_treeView(titulo):
	# create a TreeStore with one string column to use as the model
	treestore = gtk.TreeStore(str, str)

	# we'll add some data now - 4 rows with 3 child rows each
	for parent in sample(xrange(139), 7):
		piter = treestore.append(None, ['Prioridad %i' % parent, None ])
		for child in range(3):
		    treestore.append(piter, ['Proceso de prioridad %i' %
		                                  (parent), '%d' %(parent*child)])

	# create the TreeView using treestore
	treeview = gtk.TreeView(treestore)

	# create the TreeViewColumn to display the data
	tvcolumn = gtk.TreeViewColumn(titulo)

	# add tvcolumn to treeview
	treeview.append_column(tvcolumn)

	# create a CellRendererText to render the data
	cell = gtk.CellRendererText()
	cell2 = gtk.CellRendererText()

	# add the cell to the tvcolumn and allow it to expand
	tvcolumn.pack_start(cell, True)
	tvcolumn.pack_start(cell2, True)

	# set the cell "text" attribute to column 0 - retrieve text
	# from that column in treestore
	tvcolumn.add_attribute(cell, 'text', 0)
	tvcolumn.add_attribute(cell2, 'text', 1)

	# make it searchable
	treeview.set_search_column(1)

	# Allow sorting on the column
	tvcolumn.set_sort_column_id(1)

	# Allow drag and drop reordering of rows
	treeview.set_reorderable(False)

	return treeview


def botonSalir_clicked(widget):
	print "Se pulso el boton que dice.. ", widget.get_label()
	print "De paso pinto unas cosillas..."
	global drawActive
	global drawExpired

	for t in (drawActive, drawExpired):
		win = t.window
		gc = t.get_style().fg_gc[gtk.STATE_NORMAL]
		win.clear()
		X1 = 20
		X2 = 280
		Y = 15
		win.draw_rectangle(gc, False, X1, 0, X2, 15)
		for x in sample(xrange(X1, X2, 2), 17):
			win.draw_line(gc, x, 0, x, 15)
			win.draw_line(gc, x+1, 0, x+1, 15)

	if widget.get_label=="Iniciar":
		print "Rellenando campos..."

	
	
eventos = { "on_botonSalir_clicked": botonSalir_clicked,
"on_mainWindow_destroy": gtk.main_quit}

appXML = gtk.glade.XML("eppli-test1.glade")
appXML.signal_autoconnect(eventos)

mainWindow = appXML.get_widget("mainWindow")
toolbar = appXML.get_widget("toolbar")
activos = appXML.get_widget("scrollWinActive")
expirados =  appXML.get_widget("scrollWinExpired")
drawActive =  appXML.get_widget("drawActive")
drawExpired =  appXML.get_widget("drawExpired")

drawActive.set_size_request(140, 15)
drawActive.show()
drawExpired.set_size_request(140, 15)
drawExpired.show()

# Ver http://library.gnome.org/devel/gtk/2.11/gtk-Stock-Items.html
# para los iconitos stock :)

boton_play = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
boton_play.connect("clicked", botonSalir_clicked)
boton_play.set_label("Iniciar")

boton_pause = gtk.ToolButton(gtk.STOCK_MEDIA_PAUSE)
boton_pause.set_label("Pausar")
boton_pause.connect("clicked", botonSalir_clicked)

boton_stop = gtk.ToolButton(gtk.STOCK_MEDIA_STOP)
boton_stop.set_label("Detener")
boton_stop.connect("clicked", botonSalir_clicked)

boton_new = gtk.ToolButton(gtk.STOCK_ADD)
boton_new.set_label("Nuevo proceso")
boton_new.connect("clicked", botonSalir_clicked)

toolbar.add(boton_new)
toolbar.add(boton_play)
toolbar.add(boton_pause)
toolbar.add(boton_stop)

tv1 = crear_treeView("Activos")
tv2 = crear_treeView("Expirados")

activos.add_with_viewport(tv1)
expirados.add_with_viewport(tv2)

#mainWindow.connect("destroy", gtk.main_quit)	
#mainWindow.set_size_request(800, 700)
mainWindow.show_all()



res = mainWindow.show()

gtk.main()

print "Salida:", res
