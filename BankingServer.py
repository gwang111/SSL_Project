import sys
import socket
import DES
import RSA
from shared import sendMsg, recvMsg

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
		# the secret key is shared - helps confirm that the client is who they say they are
		# IRL, this would probably be some hash keyed to a user/password login
		self.secretKey = '101010101001010011'

	def SSLHandShake(self, sock):
		print('[Banking Server] Waiting For Connection From ATM...')
		connection, client_address = sock.accept()

		# Phase 1 - server receives an initial message from a client
		ret = recvMsg(connection)
		sendMsg(connection, 'Hello_back')
		print("[Banking Server] Passed Phase 1")
		
		# Phase 2 - server sends a public RSA key to the client
		e,n,d,p = RSA.generateKeys()
		pub_key = (str(e) + ' ' + str(n))
		ret = recvMsg(connection)
		sendMsg(connection, pub_key)
		print("[Banking Server] Passed Phase 2")

		# Phase 3 - server receives the shared secret key encrypted with the public key
		ret = recvMsg(connection)
		ret = ret.split()
		ret = map(int, ret)

		# we have received the secret key.
		self.secretKey = RSA.decrypt(ret,d,n)

		sendMsg(connection, 'Gotkey')
		print("[Banking Server] Passed Phase 3")

		# Phase 4 - client/server send finish messages to each other encrypted with the shared secret key.
		# client sends it first.
		plainTxt = recvMsg(connection)

		# decrypt with AES.

		# if the client's finish message is not "clientPhase4", that is not the client.
		if plainTxt != "clientPhase4":
			print('Invalid User!')
			return False, connection

		# encrypt with AES.

		sendMsg(connection, 'serverPhase4')

		print("[Banking Server] Passed Phase 4")

		# begin processing requests
		return True, connection

	def processRequests(self, connection): # <--- TODO
		# receive encrypted banking operations from ATM
		while (True):
			# initial message - rcvEncrypted?
			msg = recvMsg(connection)

			# every message should be in the format "<command> <values>"
			msg = msg.lower()
			tokens = msg.split()

			# if there is no message, then the client must have disconnected
			if msg == None:
				print("[Banking Server] Connection lost...")
				break
			# terminate the connection
			elif msg == 'e':
				print('[Banking Server] Banking Operations Successful. Exiting...')
				break
			else:
				print("[Banking Server] Processing Operation: " + msg)

				# defaults to a faulty command
				resp = "Error: Invalid Operation"
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
				sendMsg(connection, resp)


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
