from multiprocessing import Process, Queue

def inputRead(c, imps):
    imputs = []
    for i in range(len(c)):
        aux = []
        for j in range(c[i]):
            aux.append(imps[i].get())
        imputs.append(aux)
    return imputs


class Fork(Process):
    def __init__(self, imp, outs, nIter = 0):
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


class Kernel(Process):
    def __init__(self, ctrl, imps, outs, nIter = 0):
        Process.__init__(self)
        self.ctrl = ctrl    # Control input channel
        self.m = len(imps)  # Number of inputs
        self.n = len(outs)  # Number of outputs
        self.imps = imps    # List of input channels
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
            imputs = inputRead(c, self.imps)
            # Applies function to inputs
            outputs = f(imputs)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(p[i]):
                    self.outs[i].put(outputs[i][j])


class Detector(Process):
    def __init__(self, c, f, g, s0, imps, outs, nIter = 0):
        Process.__init__(self)
        self.c = c          # List of token consumption rate
        self.f = f          # Next state function
        self.g = g          # Output decoder
        self.state = s0     # Initial state
        self.m = len(imps)  # Number of inputs
        self.n = len(outs)  # Number of outputs
        self.imps = imps    # List of input channels
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
            imputs = inputRead(self.c, self.imps)
            # Performs state transition
            self.state = self.f(self.state, imputs)
            # Output decoding
            outputs = self.g(self.state)
            if len(outputs) != self.n:
                raise Exception('Function returns wrong output number')
            # Write on the output channels
            for i in range(self.n):
                for j in range(len(outputs[i])):
                    self.outs[i].put(outputs[i][j])


if __name__ == '__main__':
    print("Hello World")
    si = Queue()
    so = Queue()
    sfb = Queue()
    sd = Queue()
    sctrl = Queue()
    sko = Queue()

    def next_state(s, imps):
        if s == 1:
            if imps[0][0] > 100:
                return 2
            return 1
        else:
            if imps[0][0] < 0:
                return 1
            return 2

    def func1(a):
        return [[a[0][0] + a[1][0]]]

    def func2(a):
        return [[a[0][0] - a[1][0] - a[1][1]]]

    def out_decode(s):
        if s == 1:
            return [[([1,1], [1], func1)]]
        return [[([1,2], [1], func2)]]


    kernelProc = Kernel(sctrl, [sfb, si], [sko])
    forkProc = Fork(sko, [sfb, so, sd])
    detectorProc = Detector([1], next_state, out_decode, 1, [sd], [sctrl])
    sko.put(0)

    kernelProc.start()
    forkProc.start()
    detectorProc.start()

    for i in range(50):
        si.put(i+1)
    for i in range(50):
        print(so.get())
