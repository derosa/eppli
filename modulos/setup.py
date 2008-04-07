from distutils.core import setup, Extension

setup(name="Eppli", version = "0.1",
	ext_modules = [ Extension("eppli", ["epplimodule.c"])])

