from multiprocessing import Process, Queue

class Actor(Process):
    def __init__(self, ct, pt, f, imps, outs):
        Process.__init__(self)
        self.ct = ct        # List of token consumption rates
        self.pt = pt        # List of token production rates
        self.m = len(ct)    # Number of inputs
        self.n = len(pt)    # Number of outputs
        self.imps = imps    # List of input channels
        self.outs = outs    # List of output channels
        self.fun = f        # Function to be executed
        if len(self.imps) != self.m:
            raise Exception('Number of inputs wrong')
        if len(self.outs) != self.n:
            raise Exception('Number of outputs wrong')

    def run(self):
        while 1:
            # Reads inputs based on token consumption rates
            imputs = []
            for i in range(self.m):
                aux = []
                for j in range(self.ct[i]):
                    aux.append(self.imps[i].get())
                imputs.append(aux)
            # Applies function to inputs
            outputs = self.fun(imputs)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(self.pt[i]):
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
