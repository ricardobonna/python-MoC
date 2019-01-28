"""
Author: Ricardo Bonna
Creation date: 22/may/2018
Module description: This module provides the classes Kernel and Detector, for
creating the two basic components of an SADF model.
"""

from MoC_Core import *

class Kernel(Process):
    """
    The Kernel class creates SADF kernel processes.
    """
    def __init__(self, ctrl, inps, outs, nIter = 0):
        """
        Kernel process initializer.

        Parameters
        ----------
        ctrl : Queue
            Control channel that connects the kernel to a detector.
        inps : [Queue]
            List of input data channels.
        outs : [Queue]
            List of output data channels.
        nIter : [Int]
            Maximun number of times that the kernel is allow to fire.
            When nIter = 0 (Default), it can fire indefinitelly.
        """
        Process.__init__(self)
        self.ctrl = ctrl    # Control input channel
        self.m = len(inps)  # Number of inputs
        self.n = len(outs)  # Number of outputs
        self.inps = inps    # List of input channels
        self.outs = outs    # List of output channels
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)

    def run(self):
        n = 0
        while 1:
            if self.nIter != 0:
                n += 1
            if n > self.nIter:
                break
            # Reads the control input
            (c, p, f) = self.ctrl.get()
            # Reads inputs based on token consumption rates
            inputs = inputRead(c, self.inps)
            # Applies function to inputs
            outputs = f(inputs)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(p[i]):
                    self.outs[i].put(outputs[i][j])


class Detector(Process):
    """
    The Detector class creates SADF detector processes.
    """
    def __init__(self, c, f, g, s0, inps, outs, nIter = 0):
        """
        Detector process initializer.

        Parameters
        ----------
        c : [Int]
            List of token consumption rate.
        f : function : State, [[Tokens]] -> State
            Next state function. Returns the next state.
        g : function : State -> [[Tokens]]
            State to output function. Returns the list of outputs.
        s0 : State
            Initial state.
        inps : [Queue]
            List of input data channels.
        outs : [Queue]
            List of output control channels.
        nIter : Int (default = 0)
            Maximun number of times that the kernel is allow to fire.
            When nIter = 0, it can fire indefinitelly.
        """
        Process.__init__(self)
        self.c = c          # List of token consumption rate
        self.f = f          # Next state function
        self.g = g          # Output decoder
        self.state = s0     # Initial state
        self.m = len(inps)  # Number of inputs
        self.n = len(outs)  # Number of outputs
        self.inps = inps    # List of input channels
        self.outs = outs    # List of output channels
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)

    def run(self):
        n = 0
        while 1:
            if self.nIter != 0:
                n += 1
            if n > self.nIter:
                break
            # Reads inputs based on token consumption rates
            inputs = inputRead(self.c, self.inps)
            # Performs state transition
            self.state = self.f(self.state, inputs)
            # Output decoding
            outputs = self.g(self.state)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(len(outputs[i])):
                    self.outs[i].put(outputs[i][j])


# Test of the module
if __name__ == '__main__':
    print("SADF test model")

    def next_state(s, inps):
        if s == 1:
            if inps[0][0] > 100:
                return 2
            return 1
        else:
            if inps[0][0] < 0:
                return 1
            return 2

    def func1(a):
        return [[a[0][0] + a[1][0]]]

    def func2(a):
        return [[a[0][0] - 10]]

    def out_decode(s):
        if s == 1:
            return [[([1,1], [1], func1)]]
        return [[([1,0], [1], func2)]]

    # Definition of the channels
    si = Queue()
    so = Queue()
    sfb = Queue()
    sd = Queue()
    sctrl = Queue()
    sko = Queue()

    # Definition of the process network
    kernelProc = Kernel(sctrl, [sfb, si], [sko])
    forkProc = Fork(sko, [sfb, so, sd])
    detectorProc = Detector([1], next_state, out_decode, 1, [sd], [sctrl])
    sko.put(0)

    # Start every process in the process network
    kernelProc.start()
    forkProc.start()
    detectorProc.start()

    for i in range(50):
        si.put(i+1)

    SequencePlot(50, so)
