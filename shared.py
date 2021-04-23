import sys
import socket
import AES

# receive a message - ONLY FOR SSL HANDSHAKE
def recvMsg(sock):
	msg = ''
	try:
		while (True):
			chunk = sock.recv(1024)
			blob = chunk.decode()
			delim = blob.split()
			if delim[len(delim) - 1] != "End": msg += blob
			else:
				msg += blob[:-4]
				break
	finally:
		toks = msg.split('signature:')
		msg = toks[0]
		MAC = toks[1]
		return msg, AES.BinToSeq(MAC)
# send a message - ONLY FOR SSL HANDSHAKE
# takes in a MACdata instance along with the socket and message
def sendMsg(sock, msg, MACinfo):
	# create a MAC using AES
	MAC = AES.createMAC(msg, MACinfo)
	send_msg = msg + 'signature:' + AES.SeqToBin(MAC) + " End"
	sock.sendall(send_msg.encode())
# it is very unlikely that a cipher would produce "InitVec:" or "signature:",
# so these can be used for splitting a msg into text, i.v., and tag.
# send an encrypted message
def sendEncrypted(sock, msg, key, MACinfo):
	IV = AES.genInitVec()
	encrypted = AES.encryptMsg(msg, key, IV)
	# Generate a MAC based on the encrypted message, then attach and send it
	MAC = AES.createMAC(encrypted, MACinfo)
	# convert the sequences to a binary string for socket-friendliness (encoding is weird)
	msg = AES.SeqToBin(encrypted) + "InitVec:" + AES.SeqToBin(IV) + "signature:" + AES.SeqToBin(MAC) + ' End'
	sock.sendall(msg.encode())
# receive an encrypted message
def recvEncrypted(sock, key):
	msg, MAC = recvMsg(sock)
	toks = msg.split("InitVec:")
	# convert the binary strings back to sequences to use with AES
	cipher = AES.BinToSeq(toks[0])
	IV = AES.BinToSeq(toks[1])
	decrypted = AES.decryptMsg(cipher, key, IV)
	# return the encrypted block
	return cipher, decrypted, MAC
