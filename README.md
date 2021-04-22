## SSL PROJECT
#### By Aayush, Gary, Aidan

## How To Run:
1. Open two Linux Terminals
2. In Terminal 1: python3 BankingServer.py
3. In Terminal 2: python3 ATM.py

After the SSL Handshake finishes, you will be able to communicate with BankingServer.

## Banking Operations
w: 1000 -> withdraw $1000<br>
d: 1000 -> deposit $1000<br>
cb -> check balance

## General Operations
e -> Exit

## How To Call Crypto Algos
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
#### AES
```python
# This generates the IV in a format that works for the implementation.
IV = AES.genInitVec()
ciphertxt = AES.encryptMsg(plaintext, key, IV)
decrypted = AES.decryptMsg(ciphertxt, key, IV)
```
