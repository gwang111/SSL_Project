digests = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

def shift(dig, bits): return ((dig << bits) | (dig >> (32 - bits))) & 0xffffffff

def SHA1(msg):
    bits = ''
    dig0, dig1, dig2, dig3, dig4 = digests

    for i in range(len(msg)): bits += '{0:08b}'.format(ord(msg[i]))
    bits = bits + '1'
    padded = bits
    
    while len(padded) % 512 != 448: padded += '0'

    padded += '{0:064b}'.format(len(bits) - 1)

    for c_512 in [padded[i:i + 512] for i in range(0, len(padded), 512)]:
        a, b, c, d, e = dig0, dig1, dig2, dig3, dig4

        c_32 = [c_512[i:i + 32] for i in range(0, len(c_512), 32)]
        c_80 = [0]*80
        
        for i in range(16): c_80[i] = int(c_32[i], 2)
        for i in range(16, 80): c_80[i] = shift((c_80[i-3] ^ c_80[i-8] ^ c_80[i-14] ^ c_80[i-16]), 1)  

        for i in range(80):
            if 0 <= i <= 19: f, k = d ^ (b & (c ^ d)), 0x5A827999
            elif 20 <= i <= 39: f, k = b ^ c ^ d, 0x6ED9EBA1
            elif 40 <= i <= 59: f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
            else: f, k = b ^ c ^ d, 0xCA62C1D6
            
            temp = a
            a, e, d, c, b = shift(a, 5) + f + e + k + c_80[i] & 0xffffffff, d, c, shift(b, 30), temp

        dig0, dig1, dig2, dig3, dig4 = (dig0 + a) & 0xffffffff, (dig1 + b) & 0xffffffff, (dig2 + c) & 0xffffffff, (dig3 + d) & 0xffffffff, (dig4 + e) & 0xffffffff

    return '%08x' % (dig0) + '%08x' % (dig1) + '%08x' % (dig2) + '%08x' % (dig3) + '%08x' % (dig4)