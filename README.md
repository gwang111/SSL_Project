## SSL PROJECT
#### By Aayush, Aidan, Gary

## How To Run:
#### - Open two Linux Terminals
#### - In Terminal 2: python3 BankingServer.py
#### - In Terminal 1: python3 ATM.py
#### - For USER_NAME, use Aayush
#### - SSL HandShake Protocol Occurs
#### - Then you will be able to send banking operations to BankingServer

## Banking Operations
#### w: 1,000 -> withdraw
#### d: 1,000 -> deposit
#### cb -> check balance

## General Operations
#### E -> Exit

## How To Call Crypto Algos
#### DES
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
