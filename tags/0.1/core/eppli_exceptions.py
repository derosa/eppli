#coding: utf-8

class NotImplemented(Exception): 
    def __init__(self, func):
        self.message = "Funcion no implementada: %s" % func
    def __str__(self):
        return repr(self.message)

class NoTaskOrIdleDir(Exception):
    def __init__(self, mensaje):
        self.message = mensaje
    def __str__(self):
        return repr(self.message)