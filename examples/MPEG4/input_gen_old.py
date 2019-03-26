from typing import List, Tuple
import numpy as np



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

################### Input creation functions ####################

# uncomment the line below if you want to put these functions on a different file
# import numpy as np

# Generates a random input stream of frame types
# arguments: size = length of the output stream
#            nb = number of blocks per frame
def genFtStream(size: int, nb: int) -> List[str]:
    ft = ['I']
    for i in range(size-1):
        a = np.random.randint(0, nb)
        if a == 0:
            ft.append('I')
        else:
            ft.append('P'+str(a))
    return ft


# Generates a random input stream of macro blocs based on a list of frame types
# arguments: frameTypeList = list outputted by genFtStream
#            fs = tuple with the frame size
#            bs = block size
def genInpStream(frameTypeList: List[str], fs: Tuple[int, int], bs: int) -> List[Tuple]:
    output = []
    for i in frameTypeList:
        if i == 'I':
            output += frame2mblocks((bs,bs),(256*np.random.rand(fs[0],fs[1])).astype(int))
        elif i[0] == 'P':
            a = int(i[1:])
            posList = [np.array([a,b]) for a in range(1, fs[0] - bs + 2,bs) for b in range(1, fs[0] - bs + 2,bs)]
            output += [((256*np.random.rand(bs,bs)).astype(int), \
                posList.pop(np.random.randint(0,len(posList))), \
                (bs*np.random.rand(2) - bs/2).astype(int)) for j in range(a)]
    return output
