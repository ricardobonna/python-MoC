"""
Author: Ricardo Bonna
Creation date: 12/mar/2019
Module description: This module presents an example of an MPEG4 decoder
modeled with SADF
"""

import sys
sys.path.insert(0, '../../MoC')

from SADF import *
from input_gen import *
import numpy as np
from typing import List, Tuple
import time


################### Model parameters ####################
fs = (16,16)                      # Frame size. Each element of fs should be a multiple of bs
bs = 8                            # Macro blocks of bs x bs pixels
nb = int(fs[0]*fs[1]/(bs**2))     # Number of macro blocks in a frame


################### Auxiliary functions ####################

# Applies the Inverse Discrete Cosine Transform to a matrix inp
def idct(inp):
    size = inp.shape
    dct_matrix = np.zeros(size)
    for i in range(size[0]):
        for j in range(size[1]):
            if i == 0:
                dct_matrix[i,j] = 1/np.sqrt(2)
            else:
                dct_matrix[i,j] = np.cos((2*j+1) * i * np.pi / (2*size[0]))
    dct_matrix = dct_matrix * np.sqrt(2/size[0])
#    return inp     # Uncomment this line for testing
    return np.round(dct_matrix.transpose() @ inp @ dct_matrix).astype(int)

# block = (matrix, pos = array[row,col]).
def blockAdd(block, mat):
    pos_start = np.array([1,1])   # put [0,0] is you want the position to be 0 indexed
    b_mat = block.block
    b_pos = block.pos-pos_start
    b_size = b_mat.shape
    m_size = mat.shape
    result = np.zeros(m_size).astype(int)
    for i in range(m_size[0]):
        for j in range(m_size[1]):
            if i in range(b_pos[0], b_pos[0]+b_size[0]) and j in range(b_pos[1], b_pos[1]+b_size[1]):
                result[i,j] = mat[i,j] + b_mat[i-b_pos[0], j-b_pos[1]]
            else:
                result[i,j] = mat[i,j]
    return result




# Get a matrix x and a list of motion vecotrs and return a motion compensated matrix
# mvs = [(array(pos), array(mv))]
def motionComp(mvs, x, bs):
    x_size = x.shape
    x = frame2mblocks((bs,bs), x)
    mCompList1 = [MacroBlock(a.block, a.pos+b[1]) for a in x for b in mvs if np.array_equal(a.pos, b[0])]
    mCompList2 = [a for a in x if not any(map(lambda x: np.array_equal(a.pos,x), [b[0] for b in mvs]))]
    mCompList = mCompList1 + mCompList2
    result = np.zeros(x_size).astype(int)
    for i in mCompList:
        result = blockAdd(i,result)
    return result


# Gets a list of macro blocks [(matrix, pos = array[row,col])] and adds one by
# one to the matrix frame at the position defined by pos
def frameRC(mbl, frame):
    for i in mbl:
        frame = blockAdd(i,frame)
    return frame


################### Scenario functions definition ####################

# mb = (matrix block, pos, mv)
def scenarioVLD_func1(mbl):
    block = mbl[0][0].block
    pos = mbl[0][0].pos
    return [[MacroBlock(block, pos)], []]

def scenarioVLD_func2(mbl):
    block = mbl[0][0].block
    pos = mbl[0][0].pos
    mv = mbl[0][0].motionV
    return [[MacroBlock(block, pos)],[(pos,mv)]]

def scenarioVLD(n):
    if n == 0:
        return ([1], [1,0], scenarioVLD_func1)
    if n == 1:
        return ([1], [1,1], scenarioVLD_func2)
    else:
        raise Exception('scenarioVLD: Outside scenario range')


def scenarioIDCT_func(mbl):
    block = mbl[0][0].block
    pos = mbl[0][0].pos
    return [[MacroBlock(idct(block), pos)]]

def scenarioIDCT(n):
    if n == 1:
        return ([1], [1], scenarioIDCT_func)
    raise Exception('scenarioIDCT: Outside scenario range')


def scenarioMC_func1(inputs):
    return [[np.zeros(fs).astype(int)]]

def scenarioMC_func2(inputs):
    mvl = inputs[0]
    frame = inputs[1][0]
    return [[motionComp(mvl, frame, bs)]]

def scenarioMC(n):
    if n == 0:
        return ([0,1], [1], scenarioMC_func1)
    elif n < nb and n > 0:
        return ([n,1], [1], scenarioMC_func2)
    else:
        raise Exception('scenarioMC: Outside scenario range')


def scenarioRC_func(inputs):
    mbl = inputs[0]
    frame = inputs[1][0]
    return [[frameRC(mbl,frame)], [True]]

def scenarioRC(n):
    if n == 0:
        return ([nb,1], [1,1], scenarioRC_func)
    elif n < nb and n > 0:
        return ([n,1], [1,1], scenarioRC_func)
    else:
        raise Exception('scenarioRC: Outside scenario range')


# Next State function for detector FD
def nextStateFD(state, inps):
    token_s_ft = inps[0][0]
    token_s_fb = inps[1][0]
    if token_s_fb:
        if token_s_ft == 'I':
            nextState = 0
        elif token_s_ft[0] == 'P':
            nextState = int(token_s_ft[1:])
    return nextState


# Output decode function for detector FD
def outDecodeFD(state):
    if state == 0:
        return [[scenarioVLD(0) for i in range(nb)], [scenarioIDCT(1) for i in range(nb)], [scenarioMC(0)], [scenarioRC(0)]]
    elif state > 0 and state < nb:
        return [[scenarioVLD(1) for i in range(state)], [scenarioIDCT(1) for i in range(state)], [scenarioMC(state)], [scenarioRC(state)]]
    else:
        raise Exception('outDecodeFD: Outside scenario range')


################### Data and control channels ####################

# Data channels
s_mb = Queue()
s_db = Queue()
s_idct = Queue()
s_pf = Queue()
s_v = Queue()
s_out = Queue()
s_out1 = Queue()
s_out2 = Queue()
s_ft = Queue()
s_fb = Queue()

# Control channels
c_idct = Queue()
c_vld = Queue()
c_mc = Queue()
c_rc = Queue()

# Initial tokens
s_fb.put(True)
s_fb.put(True)
s_fb.put(True)

################### Processes ####################

# Kernels
VLD = Kernel(c_vld, [s_mb], [s_db, s_v], 0)
IDCT = Kernel(c_idct, [s_db], [s_idct], 0)
MC = Kernel(c_mc, [s_v, s_out2], [s_pf], 0)
RC = Kernel(c_rc, [s_idct, s_pf], [s_out, s_fb], 0)

# Forks
fork_out = Fork(s_out, [s_out1, s_out2], 0)

# Detector
FD = Detector([1,1], nextStateFD, outDecodeFD, 0, [s_ft, s_fb], [c_vld, c_idct, c_mc, c_rc], 0)


# each macro block is either a 2-tuple (bs x bs np.array, np.array) for I frames
#                         or a 3-tuple (bs x bs np.array, np.array, np.array) for P frames

################### Execute the module ####################

if __name__ == '__main__':
    print("MPEG4 model")

    args = sys.argv[1:] #args: fs[0] fs[1] bs nFrames

    fs = (int(args[0]), int(args[1]))
    bs = int(args[2])
    nb = int(fs[0]*fs[1]/(bs**2))
    nFrames = int(args[3])
    s_out2.put(np.zeros(fs).astype(int))

    # Generate input streams and save them
    ft = genFtStream(nFrames,nb)
    mbInputs = genInpStream(ft, fs, bs)
    saveInpsToFile(ft, mbInputs)

    # Put input signal in the input queues
    for i in ft:
        s_ft.put(i)
    for i in mbInputs:
        s_mb.put(i)

    # Start timer
    start = time.time()

    # Start the processes
    FD.start()
    VLD.start()
    IDCT.start()
    MC.start()
    RC.start()
    fork_out.start()

    # Get the outputs
    out = []
    for i in ft:
        out.append(s_out1.get())

    # Stop timer
    end = time.time()
    elapsed = round(end - start, 4)
    fps = round(nFrames/elapsed, 4)

    # Terminate the processes
    FD.terminate()
    VLD.terminate()
    IDCT.terminate()
    MC.terminate()
    RC.terminate()
    fork_out.terminate()

    print('Frame size: ' + str(fs) + '\nBlock size: ' + str(bs) + '\nNumber of frames: ' + str(nFrames) + \
        '\nTime elapsed: ' + str(elapsed) + 's' + '\nFPS: ' + str(fps))
