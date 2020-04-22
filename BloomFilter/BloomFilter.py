from helper.helper import (
    murmur3,
    encode_varint,
    int_to_little_endian,
    bit_field_to_bytes,
)
from Network.Messages import GenericMessage

BIP37_CONSTANT = 0xfba4c795


class BloomFilter:
    def __init__(self, size, function_count, tweak):
        self.size = size
        self.bit_field = [0] * (size * 8)
        self.function_count = function_count
        self.tweak = tweak

    def add(self, item):
        ''' add a item to bloom filter'''
        for i in range(self.function_count):
            seed = i * BIP37_CONSTANT + self.tweak
            h = murmur3(item, seed=seed)
            bit = h % (self.size * 8)
            self.bit_field[bit] = 1

    def filter_bytes(self):
        return bit_field_to_bytes(self.bit_field)

    def filterload(self, flag=1):
        payload = encode_varint(self.size)
        payload += self.filter_bytes()
        payload += int_to_little_endian(self.function_count, 4)
        payload += int_to_little_endian(self.tweak, 4)
        payload += int_to_little_endian(flag, 1)
        return GenericMessage(b'filterload', payload)


if __name__ == '__main__':
    field_size = 10
    bit_field_size = 8 * field_size
    bit_field = [0] * bit_field_size
    num_funcs = 5
    tweak = 99
    for item in (b'hello world', b'goodbye'):
        for i in range(num_funcs):
            seed = i * BIP37_CONSTANT + tweak
            h = murmur3(item, seed =seed)
            bit = h % bit_field_size
            bit_field[bit] = 1
    print(bit_field)

