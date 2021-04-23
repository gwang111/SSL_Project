import sys
import socket
import RSA
from shared import sendMsg, recvMsg, sendEncrypted, recvEncrypted
from AES import createMAC, MACdata, NumToSeq, SeqToNum
from secrets import randbits

class Account:
	def __init__(self, balance):
		self.balance = balance

	def deposit(self, amount):
		if amount >= 0:
			self.balance += amount
			return True
		return False

	def withdraw(self, amount):
		if self.balance >= amount and amount >= 0:
			self.balance -= amount
			return True
		return False
	
	def checkBalance(self):
		return "Account Balance For Bob is: " + str(self.balance) + " USD"

class Bank:
	def __init__(self):
		self.account = Account(1000000)

class BankingServer:
	def __init__(self):
		self.bank = Bank()
		# the secret key/MAC key are shared - helps confirm that the client is who they say they are
		# IRL, this would probably be some hash keyed to a user/password login
		# these are not known by attackers.
		self.__secretKey = '\x1a\xf4\xd5\x26\x67\xd4\x6b\xef\xc7\x25\x41\xeb\x81\xc5\x5a\x73' + \
							'\xb1\xfc\xa9\x06\x1c\xd3\xd2\x83\xe7\x15\x4c\xc3\x41\xa2\x8d\xc7'
		self.__MAC = MACdata('\x17\xb7\x3b\xb7\x7a\xdc\xae\xaf\x68\x2f\x51\x1d\x91\x61\xc5\x14' + \
							'\xcf\x46\xb1\xc8\x0d\xe0\xd5\xb1\xfb\xf9\x76\xa2\xd4\x07\xaa\x34')
		# sessionID and timeStamp are both 64 bit values that get prepended to a message during MAC
		# they are additionally unique to each session.
		self.__MAC.sessionID = 0
		# incremented before every recv
		self.__MAC.timeStamp = 0

	# helper function to check MAC address - if the original message was encrypted
	def checkMAC(self, msg, MAC):
		if createMAC(msg, self.__MAC) == MAC:
			return True
		return False

	def SSLHandShake(self, sock):
		print('[Banking Server] Waiting For Connection From ATM...')
		connection, client_address = sock.accept()

		# Phase 1 - server receives an initial message and timestamp from a client,
		#           then sends a sessionID to the client to use
		ret, MAC = recvMsg(connection)
		if not self.checkMAC(ret, MAC):
			print('[Banking Server] Failed Phase 1!')
			return False, connection
		# extract the timestamp from the sent message
		toks = ret.split(" Timestamp:")
		ret, self.__MAC.timeStamp = toks[0], int(toks[1], 16)
		print('[ATM Client]', ret, 'Timestamp:', hex(self.__MAC.timeStamp))
		# create and send a sessionID
		temp = randbits(64)
		self.__MAC.timeStamp += 1
		sendMsg(connection, 'G E N E R A L   K E N O B I ! sessionID:' + hex(temp), self.__MAC)
		print("[Banking Server] Passed Phase 1")
		self.__MAC.sessionID = temp
		
		# Phase 2 - server sends a public RSA key to the client
		e, n, d, p = None, None, None, None
		# Get a valid public and private keys
		while (True):
			e,n,d,p = RSA.generateKeys()
			test = RSA.encrypt("Test", e, n)
			test2 = RSA.decrypt(test, d, n)
			if (test2 == "Test"): break
		
		pub_key = (str(e) + ' ' + str(n))
		ret, MAC = recvMsg(connection)
		if not self.checkMAC(ret, MAC):
			print('[Banking Server] Failed Phase 2!')
			return False, connection
		self.__MAC.timeStamp += 1
		sendMsg(connection, pub_key, self.__MAC)
		print("[Banking Server] Passed Phase 2")

		# Phase 3 - server receives the shared secret key encrypted with the public key
		msg, MAC = recvMsg(connection)
		ret = msg.split()
		ret = map(int, ret)

		# check if the received key is the same as the shared secret key
		tempKey = RSA.decrypt(ret,d,n)
		if tempKey != self.__secretKey or not self.checkMAC(msg, MAC):
			print('[Banking Server] Failed Phase 3!')
			return False, connection
		self.__MAC.timeStamp += 1
		sendMsg(connection, 'KeyAck', self.__MAC)
		print("[Banking Server] Passed Phase 3")

		# Phase 4 - client/server send finish messages to each other encrypted with the shared secret key.
		# client sends it first.
		cipher, plainTxt, MAC = recvEncrypted(connection, self.__secretKey)

		# if the client's finish message is not "clientPhase4", then die.
		if plainTxt != "clientPhase4" or not self.checkMAC(cipher, MAC):
			print('[Banking Server] Failed Phase 4!')
			return False, connection

		# send a finish message back encrypted with the shared secret key.
		self.__MAC.timeStamp += 1
		sendEncrypted(connection, 'serverPhase4', self.__secretKey, self.__MAC)

		print("[Banking Server] Passed Phase 4")

		# begin processing requests
		return True, connection

	def processRequests(self, connection):
		# receive encrypted banking operations from ATM
		while (True):
			# initial message
			cipher, msg, MAC = recvEncrypted(connection, self.__secretKey)
			if not self.checkMAC(cipher, MAC):
				print('[Banking Server] Invalid MAC...')
				break

			# every message should be in the format "<command> <values>"
			msg = msg.lower()
			tokens = msg.split()

			# if there is no message, then the client must have disconnected
			if msg == None:
				print("[Banking Server] Connection lost...")
				break
			# terminate the connection
			elif msg == 'e':
				print("[ATM Client] Sent Command: " + msg)
				print('[Banking Server] Banking Operations Successful. Exiting...')
				break
			else:
				print("[ATM Client] Sent Command: " + msg)

				# defaults to a faulty command
				resp = "Error: Invalid Command"
				# withdraw:
				if tokens[0] == 'w:':
					money = 0
					try:
						money = int(tokens[1])
					except:
						resp = "Error: NaN"
					else:
						money = int(tokens[1])
						success = self.bank.account.withdraw(money)
						if success:
							resp = "Transaction Successful"
						else:
							resp = "Error: Invalid Transaction"
				# deposit:
				elif tokens[0] == 'd:': 
					money = 0
					try:
						money = int(tokens[1])
					except:
						resp = "Error: NaN"
					else:
						money = int(tokens[1])
						success = self.bank.account.deposit(money)
						if success:
							resp = "Transaction Successful"
						else:
							resp = "Error: Invalid Transaction"
				# check account balance
				elif tokens[0] == 'cb':
					resp = self.bank.account.checkBalance()
				# print whether or not the command was successful and send a response back to the client
				if resp[:7] != "Error: ":
					print("[Banking Server] Successful Command")
				else:
					print("[Banking Server] Failed Command")
				self.__MAC.timeStamp += 1
				sendEncrypted(connection, resp, self.__secretKey, self.__MAC)

	def openingServer(self):
		# Establish listening from port
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_address = ('localhost', 11111)
		print('[Banking Server] Starting Up On:', server_address[0], 'Port:', server_address[1])
		sock.bind(server_address)
		sock.listen(1)

		# perform an SSL Handshake with the client
		successful, connection = self.SSLHandShake(sock) 

		# begin listening for requests
		if successful:
			print('[Banking Server] Handshake Protocol Success. Accepting Banking Operations')
			self.processRequests(connection)
		else:
			connection.close()
			print('[Banking Server] Handshake Protocol Failed. Exiting...')
			return

def startingUp():
	server = BankingServer()
	server.openingServer()
	print('[Banking Server] Shutting Down...')

if __name__ == '__main__': startingUp()
