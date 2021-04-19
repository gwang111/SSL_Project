import binascii
from operator import xor

# JUST RUN THE SCRIPT WITH PYTHON3

# Utility Functions
#######################################################################################

def xorFunct(chunk1, chunk2):
    x = '' 
    for i in range(len(chunk1)): x += str(int(xor(bool(int(chunk1[i])), bool(int(chunk2[i])))))
    return x
    
def addPadding(msg, bit_sz):
    remainder = len(msg) % bit_sz
    if remainder != 0: return msg.zfill((bit_sz - remainder))
    return msg

def toBinary(msg):
    convert = ''
    for hexa in msg: convert += bin(int(hexa, 16))[2:].zfill(4)
    return addPadding(convert, 8)

def toHex(msg): return binascii.hexlify(bytes(msg, encoding='utf-8')).decode('utf-8')

# Simplified DES Implementation
#######################################################################################

#Generate the permutations at the beginning and end of the DES
def IFPermutation(binMsg, permutation): 
    pM = ''
    for i in permutation: pM += binMsg[i - 1]
    return pM

#Generate my key permutations
def KeyGen(initKey): 
    pTen = [ 3, 5, 2, 7, 4, 10, 1, 9, 8, 6 ]
    pEight = [ 6, 3, 7, 4, 8, 5, 10, 9 ]
    
    pKey = ''
    for i in pTen: pKey += initKey[i - 1] 
    left, right = pKey[:5], pKey[5:]
    
    lShift, rShift = left[1:] + left[0], right[1:] + right[0]
    joined = lShift + rShift

    kOne = ''
    for i in pEight: kOne += joined[i - 1]
    
    lShift, rShift = lShift[1:] + lShift[0], rShift[1:] + rShift[0]
    joined = lShift + rShift

    kTwo = ''
    for i in pEight: kTwo += joined[i - 1]

    return [kOne, kTwo]

# Function for generationg my 4 bit blocks
# Binary is evaluated LSB first
def FFunction(right, key):
    lPerm, rPerm, fPerm = '', '', ''
    perm1, perm2 = [ 4, 1, 2, 3 ], [ 2, 3, 4, 1 ]
    perm4 = [ 2, 4, 3, 1 ]
    
    s0 = [[1, 0, 3, 2], 
          [3, 2, 1, 0], 
          [0, 2, 1, 3], 
          [3, 1, 3, 2]]
    s1 = [[0, 1, 2, 3], 
          [2, 0, 1, 3], 
          [3, 0, 1, 0], 
          [2, 1, 0, 3]]

    for i in perm1: lPerm += right[i - 1]
    for i in perm2: rPerm += right[i - 1]

    eightB = lPerm + rPerm
    xored = xorFunct(eightB, key)
    
    split0, split1 = xored[:4], xored[4:]
    
    # reverse order for lsb
    col, row = int(split0[2] + split0[1], 2), int(split0[3] + split0[0], 2)
    bits1 = str(s0[row][col])
    col, row = int(split1[2] + split1[1], 2), int(split1[3] + split1[0], 2)
    bits2 = str(s1[row][col])

    # reverse order for lsb
    recombined = (bin(int(bits1, 16))[2:].zfill(2))[::-1] + (bin(int(bits2, 16))[2:].zfill(2))[::-1]

    for i in perm4: fPerm += recombined[i - 1]
    return fPerm

# Round Function that does our xoring
def Rounds(left, right, keySet):
    f1 = FFunction(right, keySet[0])
    xor1 = xorFunct(left, f1)
    f2 = FFunction(xor1, keySet[1])
    xor2 = xorFunct(right, f2)
    return xor2 + xor1

# Main Driver function to decrypt and encrypt our message
def twoRoundDES(msg, keySet):
    ip = IFPermutation(msg, [ 2, 6, 3, 1, 4, 8, 5, 7 ])
    encodeDecode = Rounds(ip[:4], ip[4:], keySet)
    fp = IFPermutation(encodeDecode, [ 4, 1, 3, 5, 7, 2, 8, 6 ])
    return fp

# Function to encrypt our plain text and then decrypt our plain text 
def SimplifiedDES(inputPlainTxt, initKey):
    keySet = KeyGen(initKey)
    
    cypherTxt = twoRoundDES(inputPlainTxt, keySet)
    print("Encrypted 8-bit Plain Text:", cypherTxt)
    retPlainTxt = twoRoundDES(cypherTxt, [keySet[1], keySet[0]])
    
    return retPlainTxt

# Pre process and split our plain text into 8bit chunks
# Stitch back together our 8bit decryptions for our original plain text
def execute(msg, initKey):
    binMsg, retMsg = toBinary(toHex(msg)), ''

    toChunk = binMsg

    print("Initial Plain Text:", binMsg)

    while len(toChunk) != 0:
        retMsg += SimplifiedDES(toChunk[:8], initKey)
        toChunk = toChunk[8:]
    
    print("Decrypted Plain Text:", retMsg)

    # Assertion to make sure our original plain text is the same as our decrypted plain text <----------------
    assert binMsg == retMsg
    print("[Assertion Passed] -> same input and decrypted plain text")

def testSuite():
    # Test case given in hw pdf
    #execute('(', '1100011110')

    key = '1100011110'
    msg = 'crypto'
    execute(msg, key)
#testSuite()
