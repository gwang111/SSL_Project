import sys
import socket
import RSA
from shared import sendMsg, recvMsg, sendEncrypted, recvEncrypted
from AES import createMAC, MACdata, NumToSeq, SeqToNum
from secrets import randbits

class ATM:
	def __init__(self):
		# not typing out 256 bits, deal with it.
		# these are not known by attackers.
		self.__secretKey = '\x1a\xf4\xd5\x26\x67\xd4\x6b\xef\xc7\x25\x41\xeb\x81\xc5\x5a\x73' + \
		'\xb1\xfc\xa9\x06\x1c\xd3\xd2\x83\xe7\x15\x4c\xc3\x41\xa2\x8d\xc7'
		self.__MAC = MACdata('\x17\xb7\x3b\xb7\x7a\xdc\xae\xaf\x68\x2f\x51\x1d\x91\x61\xc5\x14' + \
							'\xcf\x46\xb1\xc8\x0d\xe0\xd5\xb1\xfb\xf9\x76\xa2\xd4\x07\xaa\x34')
		# sessionID and timeStamp are both 64 bit values that get prepended to a message during MAC.
		# they are additionally unique to each session.
		self.__MAC.sessionID = 0
		# incremented after every send
		self.__MAC.timeStamp = 0

	# helper function to check MAC address
	def checkMAC(self, msg, MAC):
		if createMAC(msg, self.__MAC) == MAC:
			return True
		return False

	def SSLHandShake(self, sock):
		# Phase 1 - client sends an initial message, sends an initial Timestamp,
		# and receives a sessionID to use with the server.
		temp = randbits(64)
		sendMsg(sock, "Hello There. Timestamp:" + hex(temp), self.__MAC)
		self.__MAC.timeStamp = temp + 1
		ret, MAC = recvMsg(sock)
		if not self.checkMAC(ret, MAC):
			print("[ATM Client] Failed Phase 1!")
			return False
		# extract the sessionID for future use.
		toks = ret.split(" sessionID:")
		ret, self.__MAC.sessionID = toks[0], int(toks[1], 16)
		print('[Banking Server]', ret, 'sessionID:', hex(self.__MAC.sessionID))
		print("[ATM Client] Passed Phase 1")
		
		# Phase 2 - client is acknowledged and receives a public RSA key from the server.
		
		sendMsg(sock, "giveMeYourKeys", self.__MAC)
		self.__MAC.timeStamp += 1
		ret, MAC = recvMsg(sock)
		if not self.checkMAC(ret, MAC):
			print('[ATM Client] Failed Phase 2!')
			return False
		e,n = ret.split()
		print("[ATM Client] Passed Phase 2")
		
		# Phase 3 - client sends the shared secret key encrypted with the public RSA key.
		
		e, n = int(e), int(n)
		cipher = RSA.encrypt(self.__secretKey, e,n)
		# convert the RSA cipher into a string, then send it.
		cipher = map(str, cipher)
		cipher = ' '.join(cipher)

		sendMsg(sock, cipher, self.__MAC)
		self.__MAC.timeStamp += 1
		ret, MAC = recvMsg(sock)
		if not self.checkMAC(ret, MAC):
			print('[ATM Client] Failed Phase 3!')
			return False
		print("[ATM Client] Passed Phase 3")
		
		# Phase 4 - client/server send finish messages to each other encrypted with the shared secret key.

		# client -> server
		sendEncrypted(sock, 'clientPhase4', self.__secretKey, self.__MAC)
		self.__MAC.timeStamp += 1
		# server -> client
		cipher, msg, MAC = recvEncrypted(sock, self.__secretKey)

		if msg != 'serverPhase4' or not self.checkMAC(cipher, MAC):
			print('[ATM Client] That is not the server!')
			return False

		print("[ATM Client] Passed Phase 4")
		return True

	def run(self):
		# Connect to a server
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('localhost', 11111)
		print('[ATM Client] Connecting To:', server_address[0], "Port:", server_address[1])
		sock.connect(server_address)

		# perform an SSL Handshake with the server
		successful = self.SSLHandShake(sock)

		if successful:
			# Banking Operations
			# withdraw, deposit, check balance
			# Key:
			# w: 1000 -> withdraw
			# d: 1000 -> deposit
			# cb -> check balance
			# e -> Exit
			print('[ATM Client] Handshake Protocol Succeeded. Connection to Banking Server Accepted.')
			while (True):
				req = input('[ATM Client] Enter Banking Operation: ')
				sendEncrypted(sock, req, self.__secretKey, self.__MAC)
				self.__MAC.timeStamp += 1
				# terminate the connection - don't bother waiting for a response
				if req == "e":
					break
				else:
					cipher, msg, MAC = recvEncrypted(sock, self.__secretKey)
					if not self.checkMAC(cipher, MAC):
						print('[ATM Client] Invalid MAC')
						break
					print('[Banking Server]', msg)
		else:
			sock.close()
			print('[ATM Client] Handshake Protocol Failed. Denied Connection...')
			return
		sock.close()
		print('[ATM Client] Banking Operations Successful. Exiting...')

	def startATM(self):
		print('[ATM Client] Started...')
		while (True):
			op = input('[ATM Client] Type e to Exit, p to Proceed: ')
			
			if (op == 'e'):
				print('[ATM Client] Shutting off ATM...')
				break
			elif (op == 'p'):
				print('[ATM Client] Connecting to Banking Server...')

				# Handshake Protocol + Banking Operations
				self.run()
				return

def startup():
	client = ATM()
	client.startATM()
	print('[ATM Client] Shutting Down...')

if __name__ == '__main__': startup()
