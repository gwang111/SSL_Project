import sys
import socket
# TO DO: implement AES-256 (CBC mode), maybe a digital signature added as well?

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
# it is very unlikely that a cipher would produce "InitVec:" or
# "MACTag:", so these can be used for splitting a msg into text, i.v., and tag.
# send an encrypted message
def sendEncrypted(sock, msg, key):
	# AES.encrypt(msg, key)
	# msg += "InitVec:<vector>MACtag:<tag>"
	sendMsg(sock, msg)
# receive a decrypted message
def recvEncrypted(sock, key):
	msg = recvMsg(sock)
	# msg, info = msg.split("InitVec:")
	# IV, tag = info.split("MACtag:")
	# AES.decrypt(msg, key)
	return msg