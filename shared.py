import sys
import socket
# TO DO: implement AES-256 (CBC mode)

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
# send an encrypted message
def sendEncrypted(sock, msg, key):
	# AES.encrypt(msg, key)
	sendMsg(sock, msg)
# receive a decrypted message
def recvDecrypted(sock, key):
	msg = recvMsg(sock)
	# AES.decrypt(msg, key)
	return msg