import math

class BlumGoldwasser:
    def __init__(self, p, q, a, b, x0, msg):
        self.p = p
        self.q = q
        self.a = a
        self.b = b
        self.x0 = x0

        # Message
        self.msg = msg

        # init other values
        self.n = p * q
        self.block_size = int(math.log(int(math.log(self.n, 2)), 2))

    def encrypt(self):
        x_temp = self.x0
        self.crypto_txt = ''

        # Evaluate in chunks
        for split in range(len(self.msg) // self.block_size):
            start, end = split * self.block_size, (split + 1) * self.block_size
            x_temp = (x_temp ** 2) % self.n

            m_block = int(self.msg[start : end], 2)
            p_block = int(bin(x_temp)[-self.block_size:], 2)
            c_block = m_block ^ p_block
            self.crypto_txt += format(c_block, '0' + str(self.block_size) + 'b') # four bit chunks

        self.x_decrpyt = (x_temp ** 2) % self.n

    def decrypt(self):
        half1 = (self.x_decrpyt ** ((((self.q + 1) // 4)**((len(self.crypto_txt) // self.block_size) + 1)) % (self.q - 1))) % self.q
        half2 = (self.x_decrpyt ** ((((self.p + 1) // 4)**((len(self.crypto_txt) // self.block_size) + 1)) % (self.p - 1))) % self.p
        new_x = (half1 * self.a * self.p + half2 * self.b * self.q) % self.n
        x_temp = new_x
        self.dec_msg = ''

        # Evaluate in chunks
        for split in range(len(self.crypto_txt) // self.block_size):
            start, end = split * self.block_size, (split + 1) * self.block_size
            x_temp = (x_temp ** 2) % self.n

            c_block = int(self.crypto_txt[start : end], 2)
            p_block = int(bin(x_temp)[-self.block_size:], 2)
            m_block = c_block ^ p_block

            self.dec_msg += format(m_block, '0' + str(self.block_size) + 'b') # four bit chunks

    # Test encryption decryption
    def test(self):
        self.encrypt()
        self.decrypt()
        print("Original Msg:", self.msg)
        print("Encrypted Msg:", self.crypto_txt)
        print("Decrypted Msg:", self.dec_msg)
        print("Validate Original == Decrypted:", self.msg == self.dec_msg)

def main():
    msg = '010011100100010101010100010100110100010101000011'
    p, q, x0 = 499, 547, 159201
    a, b = -57, 52

    runner = BlumGoldwasser(p, q, a, b, x0, msg)
    runner.test()

#if __name__ == '__main__': main()