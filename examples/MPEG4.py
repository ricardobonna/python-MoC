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


# block = (matrix, pos = (row,col)). pos starts in (1,1)
def blockAdd(block, mat):
    b_mat = block[0]
    b_pos = block[1]
    b_size = b_mat.shape
    m_size = mat.shape
    if b_pos[0] + b_size[0] - 1 <= m_size[0] and b_pos[1] + b_size[1] - 1 <= m_size[1]:
        mat[b_pos[0]-1:b_pos[0] + b_size[0] - 1, b_pos[1]-1:b_pos[1] + b_size[1] - 1] += b_mat
    return mat




# Test of the module
if __name__ == '__main__':
    print("MPEG4 model\n")
    print(idct(np.eye(3)))

    a = np.eye(4)
    b = np.eye(2)
    print(blockAdd((b,(2,1)),a))
