#include <Python.h>
#include <string.h>

static PyObject * eppli_ffs(PyObject *self, PyObject *args)
{
	int res = 0;
	int val=0;
	if (!PyArg_ParseTuple(args, "i", &val))
		return NULL;
	res = ffs(val);
	return Py_BuildValue("i", res);
	
}

PyMethodDef methods[] = {
	{"ffs", eppli_ffs, METH_VARARGS, "Devuelve el primer bit activo de un entero"},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initeppli()
{
	(void) Py_InitModule("eppli", methods);
}

