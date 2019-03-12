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
    return dct_matrix.transpose() * inp * dct_matrix


# block = (matrix, pos = (row,col)).
def blockAdd(block, mat):
    pos_start = (1,1)   # put (0,0) is you want the position to be 0 indexed
    b_mat = block[0]
    b_pos = (block[1][0]-pos_start[0], block[1][1]-pos_start[1])
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
def frame2mblocks(d,block):
    (dr,dc) = d
    result = []
    i = 0
    while i < block.shape[0]:
        j = 0
        while j < block.shape[1]:
            result.append((np.matrix(block[i:i+dr,j:j+dc]), (i+1,j+1)))
            j+=dc
        i+=dr
    return result


# Get a matrix x and a list of motion vecotrs and return a motion compensated matrix
def motionComp(mvs, x, bs):
    return

# Test of the module
if __name__ == '__main__':
    print("MPEG4 model\n")
    print(idct(np.eye(3)))

    a = np.eye(4)
    b = np.eye(2)
    print(blockAdd((b,(0,0)),a))
    print(frame2mblocks((3,3),a))
