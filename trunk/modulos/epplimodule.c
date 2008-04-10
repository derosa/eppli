#include <Python.h>
#include <string.h>

__inline__ uint64_t rdtsc(void);


static PyObject * eppli_ffs(PyObject *self, PyObject *args)
{
	int res = 0;
	unsigned long long int val=0;
	if (!PyArg_ParseTuple(args, "l", &val))
		return NULL;
	res = ffs(val);
	return Py_BuildValue("i", res);
	
}

static PyObject *eppli_rdtsc(PyObject *self, PyObject *args)
{
	unsigned long long int res = rdtsc();
	return Py_BuildValue("l", res);
}

/*
 Función rdtsc:
 http://en.wikipedia.org/wiki/RDTSC#C
 
*/
__inline__ uint64_t rdtsc() {
	uint32_t lo, hi;
   __asm__ __volatile__ (      // serialize
     "xorl %%eax,%%eax \n        cpuid"
     ::: "%rax", "%rbx", "%rcx", "%rdx");
   /* We cannot use "=A", since this would use %rax on x86_64 */
   __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
   return (uint64_t)hi << 32 | lo;
}



PyMethodDef methods[] = {
	{"ffs", eppli_ffs, METH_VARARGS, "Devuelve el primer bit activo de un entero"},
	{"rdtsc", eppli_rdtsc, METH_VARARGS, "Devuelve TSC de la CPU"},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initeppli()
{
	(void) Py_InitModule("eppli", methods);
}

