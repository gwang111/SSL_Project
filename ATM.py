import sys
import socket
import DES
import RSA
from shared import sendMsg, recvMsg, sendEncrypted, recvEncrypted

class ATM:
	def __init__(self):
		# not typing out 256 bits, deal with it.
		self.__secretKey = '\x1a\xf4\xd5\x26\x67\xd4\x6b\xef\xc7\x25\x41\xeb\x81\xc5\x5a\x73' + \
		'\xb1\xfc\xa9\x06\x1c\xd3\xd2\x83\xe7\x15\x4c\xc3\x41\xa2\x8d\xc7'

	def SSLHandShake(self, sock):
		# TODO https://piazza.com/class_profile/get_resource/kju77hlrkbr550/kmez90r3m4w5sn?
		# Phase 1 - client sends an initial message.
		
		sendMsg(sock, "Hello")
		ret = recvMsg(sock)
		print("[ATM Client] Passed Phase 1")
		
		# Phase 2 - client is acknowledged and receives a public RSA key from the server.
		
		sendMsg(sock, "Phase 2")
		ret = recvMsg(sock)
		e,n = ret.split()
		print("[ATM Client] Passed Phase 2")
		
		# Phase 3 - client sends the shared secret key encrypted with the public RSA key.
		
		e, n = int(e), int(n)
		cipher = RSA.encrypt(self.__secretKey, e,n)
		# convert the RSA cipher into a string, then send it.
		cipher = map(str, cipher)
		cipher = ' '.join(cipher)

		sendMsg(sock, cipher)
		ret = recvMsg(sock)
		print("[ATM Client] Passed Phase 3")
		
		# Phase 4 - client/server send finish messages to each other encrypted with the shared secret key.

		# client -> server
		sendEncrypted(sock, 'clientPhase4', self.__secretKey)
		# server -> client
		msg = recvEncrypted(sock, self.__secretKey)

		if msg != 'serverPhase4':
			print('That is not the server!')
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
			print('[ATM Client] Handshake Protocol Succeeded. Connection Accepted to Banking Server')
			while (True):
				req = input('[ATM Client] Enter Banking Operation: ')
				sendEncrypted(sock, req, self.__secretKey)
				# terminate the connection - don't bother waiting for a response
				if req == "e":
					break
				else:
					print('[Banking Server]', recvEncrypted(sock, self.__secretKey))
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

