#!/usr/bin/python
# coding: utf-8

from sys import argv
from core.sched import scheduler

sched = scheduler(argv[1])

sched.run()
