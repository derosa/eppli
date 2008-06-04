#!/usr/bin/python
# coding = utf-8

NEED_RESCHED = 1

STARVATION_LIMIT = 1000

RT_RR = 0
RT_FIFO = 1
NORMAL = 2

state = {"INTERRUPTIBLE": 0, "UNINTERRUPTIBLE" : 1, "RUNNING" : 2, "EXIT" : 3}
policy = {"RR": 0, "FIFO": 1, "NORMAL": 2}

HZ = 100

TASK_DIR = "tasks"
TASK_IDLE = "idle.tsk"
