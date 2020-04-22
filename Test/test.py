from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
alice_secret_atomic_swap = "thisIsASecretPassword123".encode('utf-8')
print("Alice's secret is: ", alice_secret_atomic_swap)
print("length of Alice's secret is: ", len(alice_secret_atomic_swap))




# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332"%('abel', 'abel'))
tx_alice_id = '394cb59fedc3f2a14aeb667416bb1844ebbd0ce5658db8d99c0f4ce7505143c4'
raw = rpc_connection.getrawtransaction(tx_alice_id)
print(raw)

decode_tx = rpc_connection.decoderawtransaction(raw)
print(decode_tx)

# print(rpc_connection.getaccount('n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93')) #
# best_block_hash = rpc_connection.getbestblockhash()
# print(rpc_connection.getblock(best_block_hash))
#
# batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
# commands = [ [ "getblockhash", height] for height in range(100) ]
# block_hashes = rpc_connection.batch_(commands)
# blocks = rpc_connection.batch_([ [ "getblock", h ] for h in block_hashes ])
# block_times = [ block["time"] for block in blocks ]
# print(block_times)


# block_hash: '0000000093d5f3e8f846c86f85a1a038fd58299d0cb2dc62594c8cb74072901c'
# block_height: 1612350