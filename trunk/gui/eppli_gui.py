#!/usr/bin/python
#coding: utf-8

from core.sched import scheduler

s = scheduler("../core/tasks")
s.run()

