
class NotImplemented(Exception): 
    def __init__(self):
        self.message = "No implementado!"
    def __str__(self):
        return repr(self.message)

class NoTaskOrIdleDir(Exception):
    def __init__(self, mensaje):
        self.message = mensaje
    def __str__(self):
        return repr(self.message)