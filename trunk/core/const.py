#!/usr/bin/python
# coding = utf-8

NEED_RESCHED = 1

RT_RR = 0
RT_FIFO = 1
NORMAL = 2

# Vamos a agrupar INTERRUPTIBLE & UNINTERRUPTIBLE en un solo estado
INTERRUPTIBLE = 0
RUNNING = 1