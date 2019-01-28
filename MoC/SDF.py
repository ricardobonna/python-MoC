"""
Author: Ricardo Bonna
Creation date: 22/may/2018
Module description: This module provides the class Actor for creating
SDF actors.
"""

from MoC_Core import *

class Actor(Process):
    """
    The Actor class is used to create SDF actors.
    """
    def __init__(self, c, p, f, inps, outs, nIter = 0):
        """
        Actor process initializer.

        Parameters
        ----------
        c : [Int]
            List of token consumption rate.
        p : [Int]
            List of token production rate.
        f : function : [[Tokens]] -> [[Tokens]]
            Function executed by the actor when fired.
        inps : [Queue]
            List of input channels.
        outs : [Queue]
            List of output channels.
        nIter : Int (default = 0)
            Maximun number of times that the kernel is allow to fire.
            When nIter = 0, it can fire indefinitelly.
        """
        Process.__init__(self)
        self.c = c          # List of token consumption rates
        self.p = p          # List of token production rates
        self.m = len(c)     # Number of inputs
        self.n = len(p)     # Number of outputs
        self.inps = inps    # List of input channels
        self.outs = outs    # List of output channels
        self.fun = f        # Function to be executed
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)
        if len(self.inps) != self.m:
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
            inputs = inputRead(self.c, self.inps)
            # Applies function to inputs
            outputs = self.fun(inputs)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(self.p[i]):
                    self.outs[i].put(outputs[i][j])


# Test of the module
if __name__ == '__main__':
    print("SDF test model")
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
