"""
Author: Ricardo Bonna
Creation date: 12/mar/2019
Module description: This module presents an example of an MPEG4 decoder
modeled with SADF
"""

import sys
sys.path.insert(0, '../MoC')

from SADF import *
import numpy as np


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
    return dct_matrix.transpose() @ inp @ dct_matrix


# block = (matrix, pos = array[row,col]).
def blockAdd(block, mat):
    pos_start = np.array([1,1])   # put [0,0] is you want the position to be 0 indexed
    b_mat = block[0]
    b_pos = block[1]-pos_start
    b_size = b_mat.shape
    m_size = mat.shape
    result = np.zeros(m_size)
    for i in range(m_size[0]):
        for j in range(m_size[1]):
            if i in range(b_pos[0], b_pos[0]+b_size[0]) and j in range(b_pos[1], b_pos[1]+b_size[1]):
                result[i,j] = mat[i,j] + b_mat[i-b_pos[0], j-b_pos[1]]
            else:
                result[i,j] = mat[i,j]
    return result


# Split a large block into a listo of macro blocks of size d = (dr,dc) or smaller
def frame2mblocks(d,frame):
    (dr,dc) = d
    result = []
    i = 0
    while i < frame.shape[0]:
        j = 0
        while j < frame.shape[1]:
            result.append((frame[i:i+dr,j:j+dc], np.array([i+1,j+1])))
            j+=dc
        i+=dr
    return result


# Get a matrix x and a list of motion vecotrs and return a motion compensated matrix
# mvs = [(array(pos), array(mv))]
def motionComp(mvs, x, bs):
    x_size = x.shape
    x = frame2mblocks((bs,bs), x)
    mCompList1 = [(a[0], a[1]+b[1]) for a in x for b in mvs if np.array_equal(a[1], b[0])]
    mCompList2 = [a for a in x if not any(map(lambda x: np.array_equal(a[1],x), [b[0] for b in mvs]))]
    mCompList = mCompList1 + mCompList2
    result = np.zeros(x_size)
    for i in mCompList:
        result = blockAdd(i,result)
    return result


# Gets a list of macro blocks [(matrix, pos = array[row,col])] and adds one by
# one to the matrix frame at the position defined by pos
def frameRC(mbl, frame):
    for i in mbl:
        frame = blockAdd(i,frame)
    return frame


# Test of the module
if __name__ == '__main__':
    print("MPEG4 model\n")
    # print(idct(np.eye(3)))
    #
    # a = np.eye(4)
    # b = np.eye(2)
    # print(blockAdd((b,np.array([0,0])),a))
    # print(frame2mblocks((3,3),a))

    a = np.around(10*np.random.rand(4,4))
    print(a)
    print('\n\n')
    mvs = [(np.array([1,1]), np.array([1,0])), (np.array([3,3]), np.array([0,-1]))]
    print(motionComp(mvs,a,2))