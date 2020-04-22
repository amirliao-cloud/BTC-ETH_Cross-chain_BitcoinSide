import time
from io import BytesIO
from random import randint
from helper.helper import int_to_little_endian, little_endian_to_int, encode_varint, read_varint
from Block.Block import Block
from unittest import TestCase
import unittest

TX_DATA_TYPE = 1
BLOCK_DATA_TYPE = 2
FILTERED_BLOCK_DATA_TYPE = 3
COMPACT_BLOCK_DATA_TYPE = 4


class VersionMessage:
    command = b'version'

    def __init__(self, version=70015,
                 services=0,
                 timestamp=None,
                 receiver_services=0,
                 receiver_ip=b'\x00\x00\x00\x00',
                 receiver_port=8333,
                 sender_services=0,
                 sender_ip=b'\x00\x00\x00\x00',
                 sender_port=8333,
                 nonce=None,
                 user_agent=b'/programmingbitcoin:0.1/',
                 latest_block=0,
                 relay=False
                 ):
        self.version = version # 4 bytes, little-endian, 70015
        self.services = services # 8 bytes, little-endian
        if timestamp is None: # 8 bytes, little-endian
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.receiver_services = receiver_services # 8 bytes, little-endian
        self.receiver_ip = receiver_ip # 16 bytes
        self.receiver_port = receiver_port # 2 bytes
        self.sender_services = sender_services # 8 bytes, little-endian
        self.sender_ip = sender_ip # 16 bytes
        self.sender_port = sender_port # 2 bytes
        if nonce is None: # 8 bytes
            self.nonce = int_to_little_endian(randint(0, 2 ** 64), 8)
        else:
            self.nonce = nonce
        self.user_agent = user_agent
        self.latest_block = latest_block # current block height
        self.relay = relay # for bloom filter

    def serialize(self):
        '''Serialize this message to send over the network'''
        # version is 4 bytes little endian
        result = int_to_little_endian(self.version, 4)
        # services is 8 bytes little endian
        result += int_to_little_endian(self.services, 8)
        # timestamp is 8 bytes little endian
        result += int_to_little_endian(self.timestamp, 8)
        # receiver services is 8 bytes little endian
        result += int_to_little_endian(self.receiver_services, 8)
        # IPV4 is 10 00 bytes and 2 ff bytes then receiver ip
        result += b'\x00' * 10 + b'\xff\xff' + self.receiver_ip
        # receiver port is 2 bytes, big endian
        result += self.receiver_port.to_bytes(2, 'big')
        # sender services is 8 bytes little endian
        result += int_to_little_endian(self.sender_services, 8)
        # IPV4 is 10 00 bytes and 2 ff bytes then sender ip
        result += b'\x00' * 10 + b'\xff\xff' + self.sender_ip
        # sender port is 2 bytes, big endian
        result += self.sender_port.to_bytes(2, 'big')
        # nonce should be 8 bytes
        result += self.nonce
        # useragent is a variable string, so varint first
        result += encode_varint(len(self.user_agent))
        result += self.user_agent
        # latest block is 4 bytes little endian
        result += int_to_little_endian(self.latest_block, 4)
        # relay is 00 if false, 01 if true
        if self.relay:
            result += b'\x01'
        else:
            result += b'\x00'
        return result


class VersionMessageTest(TestCase):
    def test_serialize(self):
        v = VersionMessage(timestamp=0, nonce=b'\x00' * 8)
        self.assertEqual(v.serialize().hex(), '7f11010000000000000000000000000000000000000000000000000000000000000000000000ffff00000000208d000000000000000000000000000000000000ffff00000000208d0000000000000000182f70726f6772616d6d696e67626974636f696e3a302e312f0000000000')


class VerAckMessage:
    command = b'verack'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''


class PingMessage:
    command = b'ping'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


class PongMessage:
    command = b'pong'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


class GetHeadersMessage:
    command = b'getheaders'

    def __init__(self,
                 version=70015,
                 num_hashes=1,
                 start_block=None,
                 end_block=None):
        self.version = version
        self.num_hashes = num_hashes
        if start_block is None:
            raise RuntimeError('a start block is required')
        self.start_block = start_block
        if end_block is None:
            self.end_block = b'\x00' * 32
        else:
            self.end_block = end_block

    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(self.num_hashes)
        result += self.start_block[::-1]
        result += self.end_block[::-1]
        return result


class GetHeadersMessageTest(TestCase):
    def test_serialize(self):
        block_hex = '0000000000000000001237f46acddf58578a37e213d2a6edc4884a2fcad05ba3'
        gh = GetHeadersMessage(start_block=bytes.fromhex(block_hex))
        self.assertEqual(gh.serialize().hex(), '7f11010001a35bd0ca2f4a88c4eda6d213e2378a5758dfcd6af437120000000000000000000000000000000000000000000000000000000000000000000000000000000000')


class HeadersMessage:
    command = b'headers'

    def __init__(self, blocks):
        self.blocks = blocks

    @classmethod
    def parse(cls, stream):
        # number of headers is in a varint
        num_headers = read_varint(stream)
        # initialize the blocks array
        blocks = []
        # loop through number of headers times
        for _ in range(num_headers):
            # add a block to the blocks array by parsing the stream
            blocks.append(Block.parse_header(stream))
            # read the next varint (num_txs)
            num_txs = read_varint(stream)
            # num_txs should be 0 or raise a RuntimeError
            if num_txs != 0:
                raise RuntimeError('number of txs not 0')
        # return a class instance
        return cls(blocks)


class HeadersMessageTest(TestCase):

    def test_parse(self):
        hex_msg = '0200000020df3b053dc46f162a9b00c7f0d5124e2676d47bbe7c5d0793a500000000000000ef445fef2ed495c275892206ca533e7411907971013ab83e3b47bd0d692d14d4dc7c835b67d8001ac157e670000000002030eb2540c41025690160a1014c577061596e32e426b712c7ca00000000000000768b89f07044e6130ead292a3f51951adbd2202df447d98789339937fd006bd44880835b67d8001ade09204600'
        stream = BytesIO(bytes.fromhex(hex_msg))
        headers = HeadersMessage.parse(stream)
        self.assertEqual(len(headers.blocks), 2)
        for b in headers.blocks:
            self.assertEqual(b.__class__, Block)



class GetDataMessage:
    command = b'getdata'

    def __init__(self):
        self.data = []

    # to specify what the data we want to request
    def add_data(self, data_type, identifier):
        self.data.append((data_type, identifier))

    def serialize(self):
        result = encode_varint(len(self.data))
        for data_type, identifier in self.data:
            result += int_to_little_endian(data_type, 4)
            result += identifier[::-1]
        return result


class GetDataMessageTest(TestCase):
    def test_serialize(self):
        hex_msg = '020300000030eb2540c41025690160a1014c577061596e32e426b712c7ca00000000000000030000001049847939585b0652fba793661c361223446b6fc41089b8be00000000000000'
        get_data = GetDataMessage()
        block1 = bytes.fromhex('00000000000000cac712b726e4326e596170574c01a16001692510c44025eb30')
        get_data.add_data(FILTERED_BLOCK_DATA_TYPE, block1)
        block2 = bytes.fromhex('00000000000000beb88910c46f6b442312361c6693a7fb52065b583979844910')
        get_data.add_data(FILTERED_BLOCK_DATA_TYPE, block2)
        self.assertEqual(get_data.serialize().hex(), hex_msg)


class GenericMessage:
    def __init__(self, command, payload):
        self.command = command
        self.payload = payload

    def serialize(self):
        return self.payload


def suite():
    suite = unittest.TestSuite()
    suite.addTest(GetHeadersMessage('test_serialize'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
    # unittest.main()