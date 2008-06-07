#!/usr/bin/python
# coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

from random import sample

def pintar(cosa):
	for t in (drawActive, drawExpired):
		win = t.window
		gc = win.new_gc()
		win.clear()
		X1 = 0
		X2 = 280
		Y = 25
		celeste = win.get_colormap().alloc_color("light blue")
		rojo = win.get_colormap().alloc_color("red")

		gc.foreground = rojo
				
		win.draw_rectangle(gc, False, X1, 0, X2, Y+1)
		gc.foreground = rojo

		for x in sample(xrange(X1, X2, 2), 17):
			win.draw_line(gc, x, 0, x, Y)
			win.draw_line(gc, x+1, 0, x+1, Y)

def crear_treeView(titulo):
	# create a TreeStore with one string column to use as the model
	treestore = gtk.TreeStore(str)

	# we'll add some data now - 4 rows with 3 child rows each
	for parent in sample(xrange(139), 7):
		piter = treestore.append(None, ['Prioridad %i' % parent])
		for child in range(3):
		    treestore.append(piter, ['Proceso pepito'])

	# create the TreeView using treestore
	treeview = gtk.TreeView(treestore)

	# create the TreeViewColumn to display the data
	tvcolumn = gtk.TreeViewColumn(titulo)

	# add tvcolumn to treeview
	treeview.append_column(tvcolumn)

	# create a CellRendererText to render the data
	cell = gtk.CellRendererText()

	# add the cell to the tvcolumn and allow it to expand
	tvcolumn.pack_start(cell, True)

	# set the cell "text" attribute to column 0 - retrieve text
	# from that column in treestore
	tvcolumn.add_attribute(cell, 'text', 0)

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

	if widget.get_label=="Iniciar":
		print "Rellenando campos..."

	
def acerca_de_eppli(cosa):
	global acercade_eppli
	acercade_eppli.show()
	
eventos = { "on_botonSalir_clicked": botonSalir_clicked,
"on_mainWindow_destroy": gtk.main_quit, "on_boton_nuevo_clicked": pintar}

appXML = gtk.glade.XML("eppli-test1.glade")

mainWindow = appXML.get_widget("mainWindow")
acercade_eppli = appXML.get_widget("acercade_eppli")
toolbar = appXML.get_widget("toolbar")
activos = appXML.get_widget("scrollWinActive")
expirados =  appXML.get_widget("scrollWinExpired")
drawActive =  appXML.get_widget("drawActive")
drawExpired =  appXML.get_widget("drawExpired")
boton_nuevo = appXML.get_widget("boton_nuevo")

appXML.signal_autoconnect(eventos)

drawActive.show()
drawExpired.show()

# Ver http://library.gnome.org/devel/gtk/2.11/gtk-Stock-Items.html
# para los iconitos stock :)


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
