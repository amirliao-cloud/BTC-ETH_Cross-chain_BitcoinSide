from crypto.FieldElement import FieldElement
from crypto.Point import Point
from helper.helper import hash160, encode_base58_checksum
from unittest import TestCase
P = 2**256 - 2**32 - 977
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
A, B = 0, 7




class S256Field(FieldElement):
    def __init__(self, num, prime = None):
        super().__init__(num = num, prime = P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

    def sqrt(self):
        return self ** ((P + 1)//4)


# public key class
class S256Point(Point):
    a = None
    b = None
    def __init__(self, x, y, a, b):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __rmul__(self, coefficient):
        coef = coefficient % N
        c = super().__rmul__(coef)
        return S256Point(c.x, c.y, c.a, c.b)

    def __repr__(self):
        return 'S256Point ({}, {})'.format(self.x, self.y)

    # verify signature: (r and s), kG=R, s = (z+re)/k
    # 1: given (r, s) as signature, z as the hash of the message, P as public key
    # 2: calcualte u = z/s, v=r/s
    # 3: calculate uG + vP = R
    # 4: if the R's x-coordinate equals r, the signature is valid
    # this given public key that is a point on the secp256k1 curve and a signature hash, z,
    # we can verify whether a signature is valid or not.
    def verify(self, z, sig):
        s_inv = pow(sig.s, N - 2, N)
        u = (z * s_inv) % N
        v = (sig.r * s_inv) % N
        R = u * G + v * self
        return R.x.num == sig.r

    # Serialization (uncompressed): Standards for Efficient Cryptography (SEC)
    # 1. Start with the prefix byte, which is 0x04.
    # 2. Next, append the x coordinate in 32 bytes as a big-endian integer.
    # 3. Next, append the y coordinate in 32 bytes as a big-endian integer.

    # Serialization (compressed): Standards for Efficient Cryptography (SEC)
    # 1. Start with the prefix byte.If y is even, it’s 0x02; otherwise, it’s 0x03.
    # 2. Next, append the x coordinate in 32 bytes as a big-endian integer.
    def sec(self, compressed = True):
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x03' + self.x.num.to_bytes(32, 'big')
        else:
            return b'\x04' + self.x.num.to_bytes(32, 'big') + self.y.num.to_bytes(32, 'big')

    # when se get a serialized SEC pubkey, we can parse it to find out y
    @classmethod
    def parse(cls, sec_bin):
        if sec_bin[0] == 4:
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return cls(x = x, y = y)

        x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
        right = x ** 3 + S256Field(B)
        right_sqrt = right.sqrt()
        if right_sqrt.num % 2 == 0:
            even_y = right_sqrt
            odd_y = S256Field(P - right_sqrt.num)
        else:
            even_y = S256Field(P - right_sqrt.num)
            odd_y = right_sqrt
        if sec_bin[0] == 2:
            return S256Point(x, even_y)
        else:
            return S256Point(x, odd_y)

    def hash160(self, compressed =True):
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        '''Returns the address string'''
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'
        return encode_base58_checksum(prefix + h160)


g_x = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
g_y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

G = S256Point(g_x, g_y)


class S256Test(TestCase):
    def test_address(self):
        secret = 888 ** 3
        mainnet_address = '148dY81A9BmdpMhvYEVznrM45kWN32vSCN'
        testnet_address = 'mieaqB68xDCtbUBYFoUNcmZNwk74xcBfTP'
        point = secret * G
        self.assertEqual(
            point.address(compressed=True, testnet=False), mainnet_address)
        self.assertEqual(
            point.address(compressed=True, testnet=True), testnet_address)
        secret = 321
        mainnet_address = '1S6g2xBJSED7Qr9CYZib5f4PYVhHZiVfj'
        testnet_address = 'mfx3y63A7TfTtXKkv7Y6QzsPFY6QCBCXiP'
        point = secret * G
        self.assertEqual(
            point.address(compressed=False, testnet=False), mainnet_address)
        self.assertEqual(
            point.address(compressed=False, testnet=True), testnet_address)
        secret = 4242424242
        mainnet_address = '1226JSptcStqn4Yq9aAmNXdwdc2ixuH9nb'
        testnet_address = 'mgY3bVusRUL6ZB2Ss999CSrGVbdRwVpM8s'
        point = secret * G
        self.assertEqual(
            point.address(compressed=False, testnet=False), mainnet_address)
        self.assertEqual(
            point.address(compressed=False, testnet=True), testnet_address)


if __name__ == '__main__':
    #test = S256Test()
    #test.test_address()
    c = 2 * G
    print(g_y ** 2 % P == (g_x ** 3 + 7) % P)
    c = G + G
    print(G.y ** 2 % P == (G.x ** 3 + 7) % P)
    d = N * G
    print(c)