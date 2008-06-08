#coding: utf-8

import pygtk
pygtk.require('2.0')
import gtk

class dialogo_grafica():
    def __init__(self):
        print "toma grafica"
        self.appXML = gtk.glade.XML("gui/stat.glade")
        self.win = self.appXML.get_widget("win_stat")
        self.win.connect("delete-event", self.noop)
        self.draw = self.appXML.get_widget("draw_area")
        self.draw.connect("expose-event", self.expose)
        
        self.last_data = [(0,0)]
        self.gc = None
        
    def show(self):
        self.win.show()
        self.draw_area = self.draw.window
        self.gc = self.draw_area.new_gc()
        rojo = self.draw.get_colormap().alloc_color("red")
        self.gc.foreground = rojo
        
    def hide(self):
        self.win.hide()

    def expose(self, widget, area):
        self.update(self.last_data)
        
    def update(self, data=None):
        if not data:
            return
        else:
            self.last_data = data
            (xscale, yscale) = self.win.get_size() 
            #print  "last_data:", self.last_data
            #puntos = [(t[0]*50/xscale,yscale - t[1]*100/yscale) for (x,y) in data ]
            self.draw_area.draw_lines(self.gc, data)

    def noop(self, w, event):
        return True