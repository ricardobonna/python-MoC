"""
Author: Ricardo Bonna
Creation date: 23/may/2018
Last update: 13/mar/2019
Module description: This module provides commom functionalities used as
support for the SDF and SADF modules.
"""

from multiprocessing import Process, Queue
from typing import List
from matplotlib import pyplot

def inputRead(c, inps):
    """
    Reads the tokens in the input channels (Queues) given by the list inps
    using the token rates defined by the list c.
    It outputs a list where each element is a list of the read tokens.

    Parameters
    ----------
    c : [int]
        List of token consumption rates.
    inps : [Queue]
        List of channels.

    Returns
    ----------
    inputs: [List]
        List of token lists.
    """
    if len(c) != len(inps):
        raise Exception("Token consumption list and Queue list have different sizes")
    inputs = []
    for i in range(len(c)):
        aux = []
        for j in range(c[i]):
            aux.append(inps[i].get())
        inputs.append(aux)
    return inputs


def SequencePlot(nSamples, inp, grid = True):
    """
    Plot a sequence of nSamples from the input channel inp

    Parameters
    ----------
    nSamples: int
        Number of samples to be extracted from channel inp.
    inp: Queue
        Input channel.
    grid: bool (default = True)
        Add grid to the plot.
    """
    data = []
    for i in range(nSamples):
        data.append(inp.get())
    pyplot.plot(data, 'b.')
    if grid:
        pyplot.grid()
    pyplot.show()


class Fork(Process):
    """
    The Fork class create fork processes that are used to create channel
    junctions. A fork process replicates the tokens from its single input
    channel to its multiple output channels.
    """
    def __init__(self, inp, outs, nIter = 0):
        """
        Fork process initializer.

        Parameters
        ----------
        inp: Queue
            input channel.
        outs: [Queue]
            List of output channels.
        nIter: int (default = 0)
            Maximun number of times that the kernel is allow to fire.
            When nIter = 0, it can fire indefinitelly.
        """
        Process.__init__(self)
        self.inp = inp      # Input channel
        self.outs = outs    # List of output channels
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)

    def run(self):
        n = 0
        while 1:
            if self.nIter != 0:
                n += 1
            if n > self.nIter:
                break
            inputVal = self.inp.get()
            for i in self.outs:
                i.put(inputVal)


# Test of the module
if __name__ == '__main__':
    print("MoC_Core test model")
    c = [1]
    q = [Queue()]
    q[0].put(12)
    print(inputRead(c,q))
