"""
Author: Ricardo Bonna
Creation date: 23/mai/2018
Module description: This module provides commom functionalities used as
support for the SDF and SADF modules.
"""

from multiprocessing import Process, Queue
from typing import List

def inputRead(c: List[int], imps: List[Queue]) -> List[List]:
    """
    Reads the tokens in the input channels (Queues) given by the list imps
    using the token rates defined by the list c.
    It outputs a list where each element is a list of the read tokens.

    Parameters
    ----------
    c : List[int]
        List of token consumption rates.
    imps : List[Queue]
        List of channels.

    Returns
    ----------
    imputs: List[List]
        List of token lists.
    """
    if len(c) != len(imps):
        raise Exception("Token consumption list and Queue list have different sizes")
    imputs = []
    for i in range(len(c)):
        aux = []
        for j in range(c[i]):
            aux.append(imps[i].get())
        imputs.append(aux)
    return imputs


class Fork(Process):
    """
    The Fork class create fork processes that are used to create channel
    junctions. A fork process replicates the tokens from its single input
    channel to its multiple output channels.
    """
    def __init__(self, imp: Queue, outs: List[Queue], nIter: int = 0) -> None:
        """
        Fork process initializer.

        Parameters
        ----------
        imp: Queue
            Imput channel.
        outs: List[Queue]
            List of output channels.
        nIter: int  = 0
            Maximun number of times that the kernel is allow to fire.
            When nIter = 0, it can fire indefinitelly.
        """
        Process.__init__(self)
        self.imp = imp      # Input channel
        self.outs = outs    # List of output channels
        self.nIter = nIter  # Maximun number of firing cycles (0 means inf)

    def run(self):
        n = 0
        while 1:
            if self.nIter != 0:
                n += 1
            if n > self.nIter:
                break
            inputVal = self.imp.get()
            for i in self.outs:
                i.put(inputVal)


# Test of the module
if __name__ == '__main__':
    print("MoC_Core test model")
    c = [1]
    q = [Queue()]
    q[0].put(12)
    print(inputRead(c,q))
