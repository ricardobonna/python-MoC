from multiprocessing import Process, Queue

class Kernel(Process):
    def __init__(self, ctrl, imps, outs, nIter = 0):
        Process.__init__(self)
        self.ctrl = ctrl    # Control input channel
        self.m = len(imps)  # Number of inputs
        self.n = len(outs)  # Number of outputs
        self.imps = imps    # List of input channels
        self.outs = outs    # List of output channels
        self.nIter = nIter  # Maximun number of evaluation cycles (0 means inf)

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
            imputs = []
            for i in range(self.m):
                aux = []
                for j in range(self.c[i]):
                    aux.append(self.imps[i].get())
                imputs.append(aux)
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
