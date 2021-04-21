## SSL PROJECT
#### By Aayush, Aidan, Gary

## How To Run:
1. Open two Linux Terminals
2. In Terminal 2: python3 BankingServer.py
3. In Terminal 1: python3 ATM.py

After the SSL Handshake finishes, you will be able to communicate with BankingServer.

## Banking Operations
w: 1000 -> withdraw $1000<br>
d: 1000 -> deposit $1000<br>
cb -> check balance

## General Operations
e -> Exit

## How To Call Crypto Algos
#### DES (If its cleaner, we can use BG.py which has a straight forward encrypt() decrypt())
```python
# Given binary msg: bin_msg, msg: "Crypto"
# split into 8 bit chunks
binMsg = toBinary(toHex(msg))
cypher = ''
key = '1100011110'
toChunk = binMsg
keySet = KeyGen(key)

# For Encryption
while len(toChunk) != 0:
    cypher += twoRoundDES(toChunk[:8], keySet)
    toChunk = toChunk[8:]

# For Decryption
plainTxt = ''
while len(cypher) != 0:
    plainTxt += twoRoundDES(cypher[:8], [keySet[1], keySet[0]])
    cypher = cypher[8;]
```
#### SHA-1 Hash
#### Just call SHA1(msg) to get its digest

#### RSA
```python
e, n, d, n = generateKeys() # pub key = (e, n), priv key = (d, n)

# To Encrypt
cipher = encrypt(msg, e, n)

# To Decrypt
plainTxt = decrypt(cipher, d, n)

# if plainTxt doesn't match for some reason, do a generateKey() again and try again
# some times it acts weird and doesn't give the correct plainTxt
```
