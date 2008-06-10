#!/usr/bin/python
# coding: utf-8

from sys import argv
from core.sched import scheduler

import pycallgraph

pycallgraph.start_trace()

sched = scheduler(argv[1])

sched.run()
pycallgraph.make_dot_graph('test.png')
