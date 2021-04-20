import math
import random

def prime(n):
    for i in range(2, math.floor(math.sqrt(n))):
        if n % i == 0: return False
    return True

def gcd(a, b):
    while (b > 0): a, b = b, a % b
    return a

def modulo_inverse(e, max):
    og, track, key = max, 0, 1
    
    if (max == 1): return 0
    
    while (e > 1):
        div, temp = e // max, max

        max = e % max
        e = temp
        temp = track

        track = key - div * track
        key = temp

    if (key <= -1): key += og

    return key

def modulo(txt, key, n):
    ed, p = 1, txt % n

    for i in range(32):
        if (0x00000001 & (key >> i) == 1): ed = (ed * p) % n
        p = (p ** 2) % n
    return ed   

def gen():
    primes = [i for i in range(2, 1000) if prime(i)]
    p, q = 0, 0

    while (p == q):
        p = random.choice(primes)
        q = random.choice(primes)
    
    n = p * q

    phi = (p - 1) * (q - 1)

    es = []
    for i in range (1, phi):
        if (gcd(i, phi) == 1): es.append(i)
    e = random.choice(es)
    d = modulo_inverse(e, phi)

    return p, q, e, d, n

def generateKeys():
    p, q, e, d, n = 0, 0, 0, 0, 0
    while(e == d): p, q, e, d, n = gen()
    return e, n, d, n


def encrypt(msg, e, n):
    cipher = []
    for i in range(len(msg)): cipher.append(modulo(ord(msg[i]), e, n))
    return cipher

def decrypt(cipher, d, n):
    true_t = ''
    for i in cipher: true_t += chr(modulo(i, d, n))
    return true_t