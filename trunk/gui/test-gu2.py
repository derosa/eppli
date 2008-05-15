# coding = utf-8

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

eventos = { "on_ventana_destroy": gtk.main_quit }

xml = gtk.glade.XML("eppli-test2.glade")
xml.signal_autoconnect(eventos)

ventana = xml.get_widget("ventana")
ventana.set_size_request(800, 450)
ventana.show_all()

gtk.main()
