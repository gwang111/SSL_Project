import sys
import socket

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
	finally: return msg

def sendMsg(sock, msg):
	send_msg = msg + " End"
	sock.sendall(send_msg.encode())

# TO DO: implement AES, write sendEncrypted and rcvEncrypted