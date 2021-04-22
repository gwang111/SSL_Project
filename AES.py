from secrets import randbits

# read the s-boxes separately to save on processing power
temp = open('rijndael-forward.txt')
forward = []
for line in temp:
	forward.append(line.split())
temp.close()

temp = open('rijndael-backward.txt')
backward = []
for line in temp:
	backward.append(line.split())
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

# round constant calculated as follows: if i == 1, rcon_i = 1; else rcon_i = 2*rcon_i-1; if rcon_i-1 >= 0x80, rcon_i = rcon_i XOR 0x11b
# only the first 7 round constants are needed for 256-bit AES
rcon = [0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80]

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
		subs += Rijn_Sbox(byte)
	return subs

# generates a random 128-bit initialization vector
def genInitVec():
	return randbits(128)
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
def keySchedule(key):
	expand = key
	i, num = 0, 0
	while len(expand) < 240:
		temp = expand[-4:]
		# perform the keyscheduling core on this set of bytes
		if num % 8 == 0:
			temp = Rotate(temp)
			temp = SubMulti(temp)
			temp = chr(ord(temp[0]) ^ rcon[i]) + temp[1:]
			i += 1
		# put it through an extra s-box
		elif num % 8 == 4:
			temp = SubMulti(temp)
		# in all cases: XOR temp with the 4-byte block 32 bytes earlier
		temp = XORSeq(temp, expand[-32:-28])
		# concatenate the next 4 bytes
		expand += temp
		num += 1

	return expand
key = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'

#for i in range(0, len(subkeys), 16):
#	print(format(SeqToNum(subkeys[i:i+16]), '032x'))

# encrypts the message with AES using a 256-bit key and the given initialization vector
def encrypt(msg, key, IV):
	pass

# decrypts the message with AES using a 256-bit key and the given initialization vector
def decrypt(msg, key, IV):
	pass