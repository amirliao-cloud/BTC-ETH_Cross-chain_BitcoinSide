from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging
from Transaction.Tx import Tx, TxIn, TxOut
import requests
import json
from Transaction.Tx import TxFetcher
logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)


if __name__ == '__main__':





    # rpc_user and rpc_password are set in the bitcoin.conf file
    # rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332" % ('abel', 'abel'), timeout=120)
    # my_addr = 'n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8'
    # prev_tx_id = '0f393ef6b0af8c5e9f63bf23c75644cebe0bcb57554b547ef9ca3f992443e625'
    # prev_raw_tx = rpc_connection.getrawtransaction(prev_tx_id)
    # best_block_hash = rpc_connection.getbestblockhash()
    # print(rpc_connection.getblock(best_block_hash))
    # print(rpc_connection.getinfo())
    #
    # # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    # commands = [["getblockhash", height] for height in range(100)]
    # block_hashes = rpc_connection.batch_(commands)
    # blocks = rpc_connection.batch_([["getblock", h] for h in block_hashes])
    # block_times = [block["time"] for block in blocks]
    # print(block_times)
    tx_id = 'fbf157f19079aa0afea6648694736dbb5e2b1ee4782e6a97e52f44aabe917751'
    url_tx_fetch = '{}/txs/{}'.format(TxFetcher.get_url(testnet=True), tx_id)
    response_tx = requests.get(url_tx_fetch)
    response_tx_binary = response_tx.content
    tx_json = json.loads(response_tx_binary)
    output_script = None
    for output in tx_json['outputs']:
        if output['addresses'][0] == 'n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93':
            output_script = output['script']
    print(output_script)