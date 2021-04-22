import sys
import socket
import AES
# TO DO: implement AES-256 (CBC mode), maybe a digital signature added as well?
# For MAC, add seconds passed + session id -> gives uniqueness to each MAC

# receive a message - ONLY FOR SSL HANDSHAKE
def recvMsg(sock):
	msg = ''
	try:
		while (True):
			chunk = sock.recv(1024)
			delim = chunk.decode().split()
			if delim[len(delim) - 1] != "End": msg += ' '.join(delim)
			else: 
				msg += ' '.join(delim[:-1])
				break
	finally:
		return msg
# send a message - ONLY FOR SSL HANDSHAKE
def sendMsg(sock, msg):
	send_msg = msg + " End"
	sock.sendall(send_msg.encode())
# it is very unlikely that a cipher would produce "InitVec:" or "MACTag:",
# so these can be used for splitting a msg into text, i.v., and tag.
# send an encrypted message
def sendEncrypted(sock, msg, key):
	IV = AES.genInitVec()
	encrypted = AES.encryptMsg(msg, key, IV)
	# convert the sequences to a binary string for socket-friendliness (encoding is weird)
	encrypted = AES.SeqToBin(encrypted) + "InitVec:" + AES.SeqToBin(IV)
	# msg += "InitVec:<vector>MACtag:<tag>"
	sendMsg(sock, encrypted)
# receive an encrypted message
def recvEncrypted(sock, key):
	msg = recvMsg(sock)
	toks = msg.split("InitVec:")
	# convert the binary string back to a sequence to use with AES
	seq = AES.BinToSeq(toks[0])
	IV = AES.BinToSeq(toks[1])
	# IV, tag = info.split("MACtag:")
	decrypted = AES.decryptMsg(seq, key, IV)
	return decrypted
