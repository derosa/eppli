#coding:utf-8

import pygtk
import gtk
from pychart import *
import StringIO

class eppli_graph_stats():
    def __init__(self):
        theme.use_color = 1
        theme.default_font_size = 12
        theme.reinitialize()

        self.xaxis="Eje X"
        self.yaxis="Eje Y"
        self.w = 600
        self.h = 400
    
    def set_axis_title(self, x, y):
        self.xaxis=x
        self.yaxis=y
        
    def get_max(self, data):
        ys = (y for (x,y) in data)
        xs = (x for (x,y) in data)
        x = max(xs)
        y = max(ys)
        return (x,y)
    
    def generate_graph(self, datos_proc):
        """ Devuelve un pixbuf a partir de los datos para la gráfica"""
        # Buffer donde generar el gráfico
        tmp_data = StringIO.StringIO()
        
        # Lienzo en formato SVG
        can = canvas.init(tmp_data, "svg")
        size = (width,height) = (self.w, self.h)
        
        # Máxima altura de los datos
        max_x,max_y = self.get_max(datos_proc)
        
        ar = area.T(size = (self.w-50, self.h-50), 
                    y_grid_interval=max_y/10.0,
                    x_grid_interval=max_x/10.0,
                    legend=None, 
                    y_range = (0.1, max_y*1.10),
                    x_range = (0.1, max_x*1.10),
                    x_axis = axis.X(format="/12/H%.2f", label=self.xaxis),
                    y_axis = axis.Y(format="/12/H%.2f", label=self.yaxis)) 
        
        ar.add_plot(line_plot.T(data=datos_proc))
        ar.draw()

        # can.show(ar.x_pos(4), ar.y_pos(9070), "/a45{}Grafiquito")
        can.close()
        
        buffer = tmp_data.getvalue()
        tmp_data.close()
        if not buffer:
            print "El buffer está vacío....!"
        # Se carga el gráfico en la imagen pasada como parámetro
        loader = gtk.gdk.PixbufLoader ('svg')
        loader.set_size(width, height)
        loader.write( buffer )
        loader.close()

        buffer = loader.get_pixbuf()
        return buffer
