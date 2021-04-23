from secrets import randbits

class MACdata:
	def __init__(self, key):
		self.key = key
		self.sessionID = 0
		self.timeStamp = 0

# read data separately to save on processing power
# forward Rijndael S-box
temp = open('rijndael-forward.txt')
forward = []
for line in temp:
	forward.append(line.split())
temp.close()

# backward Rijndael S-box
temp = open('rijndael-backward.txt')
backward = []
for line in temp:
	backward.append(line.split())
temp.close()

# round constant calculated as follows: if i == 1, rcon_i = 1; else rcon_i = 2*rcon_i-1; if rcon_i-1 >= 0x80, rcon_i = rcon_i XOR 0x11b
# only the first 7 round constants are needed for 256-bit AES key expansion
rcon = [0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80]

# Galois(2^8) multiplication lookup tables
# times 0x2
temp = open('mix2.txt')
mul2 = [int(num, 16) for num in temp.read().split()]
temp.close()
# times 0x3
temp = open('mix3.txt')
mul3 = [int(num, 16) for num in temp.read().split()]
temp.close()
# times 0x9
temp = open('mix9.txt')
mul9 = [int(num, 16) for num in temp.read().split()]
temp.close()
# times 0xB
temp = open('mixB.txt')
mulB = [int(num, 16) for num in temp.read().split()]
temp.close()
# times 0xD
temp = open('mixD.txt')
mulD = [int(num, 16) for num in temp.read().split()]
temp.close()
# times 0xE
temp = open('mixE.txt')
mulE = [int(num, 16) for num in temp.read().split()]
temp.close()

# convert a sequence of bytes (chars) into its bit-string equivalent
def SeqToBin(sequence):
	binary = ''.join(format(ord(char), '08b') for char in sequence)
	return binary

# convert a bit-string into a sequence of bytes. ONLY USE THIS TO UNDO toBin!
def BinToSeq(binary):
	byte = binary
	sequence = ''
	while not byte == '':
		temp = byte[:8]
		sequence += chr(int(temp, 2))
		byte = byte[8:]
	return sequence

# converts a number to a sequence and optionally adds leading zeros given a minimum size
def NumToSeq(number, min_size=0):
	# go through 1 hex byte at a time
	temp = hex(number)[2:]
	seq = ''
	# go in reverse order, to account for leading zeros.
	for i in range(len(temp), 0, -2):
		seq = chr(int(temp[max(i-2, 0):i], 16)) + seq
	# add leading zeros to get to the specified minimum size
	while not len(seq) >= min_size:
		seq = '\x00' + seq
	return seq

# converts a sequence to a number equivalent.
def SeqToNum(sequence):
	temp = ''
	for byte in sequence:
		temp += hex(ord(byte))[2:]
	return int(temp, 16)

# perform an XOR between two sequences of equal length.
# because of the nature of XOR, it can be split up between each byte (no carrying)
def XORSeq(seq1, seq2):
	xor = ''
	for i in range(len(seq1)):
		xor += chr(ord(seq1[i]) ^ ord(seq2[i]))
	return xor

# performs a circular left shift of 8 bits (1 byte) on the byte sequence
def Rotate(sequence):
	return sequence[1:] + sequence[0]

# perform a forward or backward Rijndael S-box substitution on the given byte
def Rijn_Sbox(byte,direction='f'):
	# get the hex representation of the number
	nibbles = format(ord(byte), '02x')
	# top half is row, bottom half is column
	row = int(nibbles[0], 16)
	col = int(nibbles[1], 16)

	# returns a string byte
	if direction == 'f':
		return chr(int(forward[row][col],16))
	else:
		return chr(int(backward[row][col],16))

# perform a forward or backward Rijndael S-box substitution on every byte in the sequence
def SubMulti(sequence, direction='f'):
	subs = ''
	for byte in sequence:
		subs += Rijn_Sbox(byte, direction)
	return subs

# generates a random 128-bit initialization vector in byte sequence form
def genInitVec():
	bits = randbits(128)
	vec = ''
	for i in range(0, 128, 8):
		# shift right i bits
		temp = bits >> i
		value = 0xff & temp
		vec = chr(value) + vec

	return vec

# generate subkeys for use with AES using the given key
# the algorithm is as follows:
# 
# Schedule Core:
#     input 4 bytes and it_num i, output 4 bytes
#     output = Rotate(input)
#     output = SubMulti(output)
#     output[0] = output[0] XOR rcon[i]

# First 32 bytes are just the key.
# Until we have 15*16 = 240 bytes, do the following:
#     temp = <last 4 bytes of expanded key>

#     bytes 00-03 of every 32 bytes (mod 8 equiv 0):
#         temp = ScheduleCore(temp, i)
#         i += 1
#     bytes 16-19 of every 32 bytes (mod 8 equiv 4):
#         temp = SubMulti(last 4 bytes of expanded key)

#     temp = temp XOR <4 bytes that are 32 bytes earlier>
#     add temp to expanded key

# The keys have to be the same for both encryption and decryption,
# so only forward passes through the s-boxes are used either way.
def keyExpand(key):
	expand = key
	i, num = 0, 0
	while len(expand) < 240:
		# every 32 bytes, certain bytes get extra ops done
		temp = expand[-4:]
		# perform the keyscheduling core on bytes 0-3
		if num % 8 == 0:
			temp = Rotate(temp)
			temp = SubMulti(temp)
			temp = chr(ord(temp[0]) ^ rcon[i]) + temp[1:]
			i += 1
		# put bytes 16-19 through an extra s-box
		elif num % 8 == 4:
			temp = SubMulti(temp)
		# in all cases: XOR temp with the 4-byte block 32 bytes earlier
		temp = XORSeq(temp, expand[-32:-28])
		# concatenate the next 4 bytes
		expand += temp
		num += 1
	# split the stream into 15 16-byte subkeys before returning it
	return [expand[i:i+16] for i in range(0, len(expand), 16)]

# converts a 16-byte block into a column-major 4x4 table
def BlockToTable(block):
	table = [[], [], [], []]
	i = 0
	for char in block:
		table[i % 4].append(char)
		i += 1

	return table

# converts a column-major 4x4 table into a 16-byte block
def TableToBlock(table):
	sequence = ''
	for r in range(4):
		for c in range(4):
			sequence += table[c][r]

	return sequence

# searches the appropriate lookup table and returns the corresponding value
def lookup(coeff, val):
	result = val
	# check if multiply by 2, 3, 9, 11, 13, or 14 resp.
	# default is multiply by 1
	if coeff == 2:
		result = mul2[val]
	elif coeff == 3:
		result = mul3[val]
	elif coeff == 9:
		result = mul9[val]
	elif coeff == 11:
		result = mulB[val]
	elif coeff == 13:
		result = mulD[val]
	elif coeff == 14:
		result = mulE[val]
	return result

# performs a column mix on the 4x4 table to distribute s-box nonlinearity
# essentially performs the following matrix operation under Galois(2^8):
# [d_0]   [2 3 1 1][b_0]    d_0 = 2*b_0 + 3*b_1 + 1*b_2 + 1*b_3
# [d_1] = [1 2 3 1][b_1] -> d_1 = 1*b_0 + 2*b_1 + 3*b_2 + 1*b_3
# [d_2] = [1 1 2 3][b_2] -> d_2 = 1*b_0 + 1*b_1 + 2*b_2 + 3*b_3
# [d_3]   [3 1 1 2][b_3]    d_3 = 3*b_0 + 1*b_1 + 1*b_2 + 2*b_3
# d is the newly encrypted form. Remember that + is equivalent to XOR in Galois(2^8)!
# for simplicity's sake, multiplication has been converted to lookup tables -> 2*value = tbl_2[value]
def MixColumns(table):
	coeffs = [[2, 3, 1, 1],
			  [1, 2, 3, 1],
			  [1, 1, 2, 3],
			  [3, 1, 1, 2]]
	new_table = [[0, 0, 0, 0],
				 [0, 0, 0, 0],
				 [0, 0, 0, 0],
				 [0, 0, 0, 0]]
	# for each column in the original table
	for i in range(4):
		# for each row/col in the coefficient matrix
		for j in range(4):
			for k in range(4):
				new_table[j][i] ^= lookup(coeffs[j][k], ord(table[k][i]))
	# converts the new table into byte representations
	return [[chr(entry) for entry in row] for row in new_table]

# inverts a column mix on the 4x4 table to ready it for inverse s-box
# essentially performs the following matrix operation under Galois(2^8):
# [b_0]   [14 11 13 09][d_0]    b_0 = 14*d_0 + 11*d_1 + 13*d_2 + 09*d_3
# [b_1] = [09 14 11 13][d_1] -> b_1 = 09*d_0 + 14*d_1 + 11*d_2 + 13*d_3
# [b_2] = [13 09 14 11][d_2] -> b_2 = 13*d_0 + 09*d_1 + 14*d_2 + 11*d_3
# [b_3]   [11 13 09 14][d_3]    b_3 = 11*d_0 + 13*d_1 + 09*d_2 + 14*d_3
# b is the newly decrypted form. Remember that + is equivalent to XOR in Galois(2^8)!
# for simplicity's sake, multiplication has been converted to lookup tables
def InvColumns(table):
	coeffs = [[14, 11, 13, 9],
			  [9, 14, 11, 13],
			  [13, 9, 14, 11],
			  [11, 13, 9, 14]]
	new_table = [[0, 0, 0, 0],
				 [0, 0, 0, 0],
				 [0, 0, 0, 0],
				 [0, 0, 0, 0]]
	# for each column in the original table
	for i in range(4):
		# for each row/col in the coefficient matrix
		for j in range(4):
			for k in range(4):
				new_table[j][i] ^= lookup(coeffs[j][k], ord(table[k][i]))
	return [[chr(entry) for entry in row] for row in new_table]

# performs circular shifts on the rows of the 4x4 table.
# left for rev = False (encryption), right for rev = True (decryption)
# the nth row gets shifted n times, for n = 0 to len(table)-1.
def ShiftRows(table, rev=False):
	new_table = table
	for n in range(len(table)):
		t_row = new_table[n]
		# 0 iterations for row 0, 1 iteration for row 1, etc.
		for _ in range(n):
			# are we decrypting?
			if rev:
				# pop the last val, then insert it at the beginning.
				temp = t_row.pop()
				t_row.insert(0, temp)
			# we are encrypting.
			else:
				# store the first val, then move the list up one. append the stored value.
				temp = t_row[0]
				t_row = t_row[1:]
				t_row.append(temp)
		# assign the new row to the table
		new_table[n] = t_row

	return new_table

# performs AES encryption on a 16-byte/128-bit block
# high-level description - AES treats 16-byte blocks as 4x4 arrays
# 1. keyExpansion - this is handled in AES.encrypt()
# 2. initial round key addition
# 3. for 13 rounds, do the following:
#    a. SubBytes - perform forward S-box on every byte
#    b. ShiftRows - the last 3 rows are cyclically shifted N steps (rows 0-3)
#    c. MixColumns - combine the 4 columns using an invertible transformation
#    d. add a round key
# 4. Final round
#    a. SubBytes
#    b. ShiftRows
#    c. add the last round key
# returns the encrypted byte sequence
def blockEnc(block, subkeys):
	# initial addition
	i = 0
	encrypted = XORSeq(block, subkeys[i])
	# go to the next subkey in the sequence
	i += 1
	# SubBytes -> ShiftRows -> MixColumns -> XOR -> repeat 13 times
	for _ in range(13):
		encrypted = SubMulti(encrypted, 'f')
		enc_table = BlockToTable(encrypted)
		# ShiftRows
		enc_table = ShiftRows(enc_table, rev=False)
		# MixColumns - this distributes the S-box's nonlinearity
		enc_table = MixColumns(enc_table)
		encrypted = TableToBlock(enc_table)
		encrypted = XORSeq(encrypted, subkeys[i])
		i += 1
	# final round - i should be 14 at this point
	encrypted = SubMulti(encrypted, 'f')
	# ShiftRows
	enc_table = BlockToTable(encrypted)
	enc_table = ShiftRows(enc_table, rev=False)
	encrypted = TableToBlock(enc_table)

	encrypted = XORSeq(encrypted, subkeys[i])
	return encrypted

# performs AES decryption on a 16-byte/128-bit block.
# note that decryption travels the subkeys in reverse order.
# Decryption is essentially applying every inverse operation in reverse order.
# Due to the non-uniformity of AES encryption, decryption must be separate.
# returns the decrypted byte sequence
def blockDec(block, subkeys):
	# inverse final round
	i = len(subkeys)-1
	decrypted = XORSeq(block, subkeys[i])
	# ShiftRows
	dec_table = BlockToTable(decrypted)
	dec_table = ShiftRows(dec_table, rev=True)
	decrypted = TableToBlock(dec_table)
	# use the backwards Rijndael S-box
	decrypted = SubMulti(decrypted, 'b')
	for _ in range(13):
		i -= 1
		decrypted = XORSeq(decrypted, subkeys[i])
		dec_table = BlockToTable(decrypted)
		# InvColumns - this restores the original S-box permutation
		dec_table = InvColumns(dec_table)
		# ShiftRows
		dec_table = ShiftRows(dec_table, rev=True)
		decrypted = TableToBlock(dec_table)
		decrypted = SubMulti(decrypted, 'b')
	# inverse first round - i should be 1 by this point
	i -= 1
	decrypted = XORSeq(decrypted, subkeys[i])
	return decrypted


# encrypts the message with AES using a 256-bit key and the given initialization vector
def encryptMsg(msg, key, IV):
	subkeys = keyExpand(key)
	# split message into 16-byte blocks
	blocks = []
	for i in range(0, len(msg), 16):
		b = msg[i:i+16]
		# pad with pad length if we don't have enough space
		if len(b) < 16:
			pad = 16-len(b)
			b += chr(pad)*pad
		blocks.append(b)

	encrypted = ''
	prev = IV
	for block in blocks:
		# XOR the current block with the previous one, beginning with prev = IV
		chain = XORSeq(block, prev)
		cipher = blockEnc(chain, subkeys)
		encrypted += cipher
		prev = cipher

	return encrypted


# decrypts the message with AES using a 256-bit key and the given initialization vector
def decryptMsg(msg, key, IV):
	subkeys = keyExpand(key)
	# split message into 16-byte blocks - decryption, so no padding needed
	blocks = []
	for i in range(0, len(msg), 16):
		b = msg[i:i+16]
		blocks.append(b)

	decrypted = ''
	prev = IV
	for block in blocks:
		chain = blockDec(block, subkeys)
		decrypted += XORSeq(chain, prev)
		prev = block
	# get the last block and check for padding
	last_block = decrypted[-16:]
	for i in range(len(last_block)):
		# we are padding with pad length - filter out padding if we have a match
		if ord(last_block[i]) == 16-i:
			decrypted = decrypted[:-1 * (16-i)]

	return decrypted

# creates a CBC MAC - note: Never use the same key as the actual encrypted message.
def createMAC(msg, MACinfo):
	ID, Stamp = NumToSeq(MACinfo.sessionID, 8), NumToSeq(MACinfo.timeStamp, 8)
	# encrypt using the zero vector for initialization and a prepended ID/Stamp
	chain = encryptMsg(ID + Stamp + msg, MACinfo.key, '\x00'*16)
	# take the last block and use it as the MAC address
	MAC = chain[-16:]
	return MAC

# some code to test a full AES encryption and decryption with padding.
if __name__ == '__main__':
	message = 'My name is Yoshikage Kira. I\'m 33 years old.'
	message = 'clientPhase4'
	key = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
	IV = genInitVec()

	print(message)
	encrypted = encryptMsg(message, key, IV)
	encrypted = SeqToBin(encrypted)
	encrypted = BinToSeq(encrypted)
	decrypted = decryptMsg(encrypted, key, IV)
	print('decrypted:')
	print(decrypted)