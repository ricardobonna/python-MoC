"""
Author: Ricardo Bonna
Creation date: 22/mai/2018
Module description: This module provides the class Actor for creating SDF actors.
"""

from MoC_Core import *

class Actor(Process):
    """
    The Actor class is used to create SDF actors.
    """
    def __init__(self, c, p, f, imps, outs, nIter = 0):
        Process.__init__(self)
        self.c = c          # List of token consumption rates
        self.p = p          # List of token production rates
        self.m = len(c)     # Number of inputs
        self.n = len(p)     # Number of outputs
        self.imps = imps    # List of input channels
        self.outs = outs    # List of output channels
        self.fun = f        # Function to be executed
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)
        if len(self.imps) != self.m:
            raise Exception('Number of inputs wrong')
        if len(self.outs) != self.n:
            raise Exception('Number of outputs wrong')

    def run(self):
        n = 0
        while 1:
            if self.nIter != 0:
                n += 1
            if n > self.nIter:
                break
            # Reads inputs based on token consumption rates
            imputs = inputRead(self.c, self.imps)
            # Applies function to inputs
            outputs = self.fun(imputs)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(self.p[i]):
                    self.outs[i].put(outputs[i][j])


if __name__ == '__main__':
    print("Hello World")
    q1 = Queue()
    q2 = Queue()

    def func_test(a):
        return [[a[0][0]+a[0][1], a[0][0]-a[0][2]]]

    proc = Actor([3], [2], func_test, [q1], [q2])
    proc.start()

    for i in range(6):
        q1.put(i+1)
    print(q2.get())
    print(q2.get())
    print(q2.get())
    print(q2.get())
