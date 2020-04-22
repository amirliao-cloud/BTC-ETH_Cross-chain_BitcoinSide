from Network.NetworkEnvelope import NetworkEnvelope
from Network.Messages import (
    HeadersMessage,
    GetDataMessage,
    GetHeadersMessage,
    FILTERED_BLOCK_DATA_TYPE
)
from Network.SimpleNode import SimpleNode
from Block.Block import Block, GENESIS_BLOCK, LOWEST_BITS
from io import BytesIO
from helper.helper import calculate_new_bits, decode_base58
from BloomFilter.BloomFilter import BloomFilter
from MerkleBlock.MerkleBlock import MerkleBlock
from Transaction.Transaction import Tx

if __name__ == '__main__':

    # get headers
    previous = Block.parse(BytesIO(GENESIS_BLOCK))
    first_epoch_timestamp = previous.timestamp
    expected_bits = LOWEST_BITS
    count = 1

    # for _ in range(19):
    #     getheaders = GetHeadersMessage(start_block=previous.hash())
    #     node.send(getheaders)
    #     headers = node.wait_for(HeadersMessage)
    #     for header in headers.blocks:
    #         if not header.check_pow():
    #             raise RuntimeError('bad PoW at block {}'.format(count))
    #         if header.prev_block!= previous.hash():
    #             raise RuntimeError('discontinuous block at {}'.format(count))
    #         if count % 2016 == 0:
    #             time_diff = previous.timestamp - first_epoch_timestamp
    #             expected_bits = calculate_new_bits(previous.bits, time_diff)
    #             print(expected_bits.hex())
    #             first_epoch_timestamp = header.timestamp
    #         if header.bits != expected_bits:
    #             raise RuntimeError('bad bits at block {}'.format(count))
    #         previous = header
    #         count += 1

    # get transactions of interest
    last_block_hex = '00000000000538d5c2246336644f9a4956551afb44ba47278759ec55ea912e19'
    address = 'mwJn1YPMq7y5F8J3LkC5Hxg9PHyZ5K4cFv'
    h160 = decode_base58(address)
    bf = BloomFilter(size = 30, function_count=5, tweak=90210)
    bf.add(h160)
    node = SimpleNode('mainnet.programmingbitcoin.com', testnet=False)
    node.handshake()
    node.send(bf.filterload())
    start_block = bytes.fromhex(last_block_hex)
    getheaders = GetHeadersMessage(start_block=start_block)
    node.send(getheaders)
    headers = node.wait_for(HeadersMessage)
    for header in headers.blocks:
        if not header.check_pow():
            raise RuntimeError('bad PoW at block {}'.format(count))
        if header.prev_block!= previous.hash():
            raise RuntimeError('discontinuous block at {}'.format(count))
        if count % 2016 == 0:
            time_diff = previous.timestamp - first_epoch_timestamp
            expected_bits = calculate_new_bits(previous.bits, time_diff)
            print(expected_bits.hex())
            first_epoch_timestamp = header.timestamp
        if header.bits != expected_bits:
            raise RuntimeError('bad bits at block {}'.format(count))

    getdata = GetDataMessage()
    for b in headers.blocks:
        if not b.check_pow():
            raise RuntimeError('proof of work is invalid')
        getdata.add_data(FILTERED_BLOCK_DATA_TYPE, b.hash())
    node.send(getdata)
    found = False
    while not found:
        message = node.wait_for(MerkleBlock, Tx)
        if message.command == b'merkleblock':
            if not message.is_valid():
                raise RuntimeError('invalid merkle proof')
            else:
                for i, tx_out in enumerate(message.tx_outs):
                    if tx_out.script_pubkey.address(testnet=True) == address:
                        print('found: {}:{}'.format(message.id(), i))
                        found = True
                        break
