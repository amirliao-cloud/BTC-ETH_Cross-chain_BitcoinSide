from helper.helper import (
    little_endian_to_int,
    hash256,
    decode_base58,

)
from crypto.Signature import PrivateKey
from Scripts.Script import p2pkh_script, p2sh_script
from Transaction.Tx import Tx, TxIn, TxOut
import requests
import json
from Transaction.Tx import TxFetcher

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Abel's private key is:  <crypto.Signature.PrivateKey object at 0x000002142A6CC0F0>
# Abel's address is:  n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8
# Alice's private key is:  <crypto.Signature.PrivateKey object at 0x000002142A851B38>
# Alice's address is:  n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93
# Bob's private key is:  <crypto.Signature.PrivateKey object at 0x000002142AA79C50>
# Bob's address is:  mtP5yN9q6bFdiWqwcDJsiobPBVVFdwQTvR




if __name__ == '__main__':



    # get the current testnet block ID
    # send yourself some testnet coins
    # find the UTXO corresponding to the testnet coins
    # create a transaction using that UTXO as an input
    # broadcast the tx message on the testnet
    # secret = little_endian_to_int(hash256(b'abelyang@astri.org'))
    # private_key = PrivateKey(secret=secret)
    # public_key = private_key.point.sec()
    # # private_key: cUz2mXMT2jyqdwXuFeZgy71tvF96vnvAmH8KvtsMdzhY2AtrJUJv
    # my_addr = private_key.point.address(testnet=True)

    my_addr = 'n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93'
    #my_addr = 'n4kJxHoZC9uTjfYAmeXSnHP9ss6YqiQja8'
    my_addr_h160 = decode_base58(my_addr) # hash160 of the public key

    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332" % ('abel', 'abel'), timeout=120)

    #
    # tx_id = '5672a8a88956862717b8b8c6d8001e8d64fa103b91bec95aba6c1fdea54021af'
    # raw = bytes.fromhex(rpc_connection.getrawtransaction(tx_id))

    fee = int(0.00005 * 100000000)
    pay_amount = int(0.01 * 100000000)
    prev_tx, prev_index, prev_amount, prev_output_script = None, None, None, None
    # prev_tx can be fetched via API or just write here

    # get all transactions history on an Address
    # 'https://api.blockcypher.com/v1/btc/test3'
    url_addr_history = '{}/addrs/{}/full'.format(TxFetcher.get_url(testnet=True), my_addr)
    response_addr_history = requests.get(url_addr_history)
    response_addr_history_binary = response_addr_history.content
    addr_history_json = json.loads(response_addr_history_binary)
    # since a tx has multiple outputs to cover the pay_amount, we only consider the output that has sufficient coins
    if addr_history_json['balance'] < pay_amount + fee:
        print('The balance of address %s is not enough to cover the payment', my_addr)
    for tx_info in addr_history_json['txs']:
        if prev_tx is not None:
            break
        for i, output in enumerate(tx_info['outputs']):
            if output['value'] >= pay_amount + fee and output['addresses'][0] == my_addr:
                prev_tx = tx_info['hash']
                prev_index = i
                prev_amount = output['value']
                prev_output_script = output['script']
                break
    print(prev_tx)
    # prev_tx = '0f393ef6b0af8c5e9f63bf23c75644cebe0bcb57554b547ef9ca3f992443e625'
    # use bitcoin RPC API to get the raw transaction
    # response_tx = TxFetcher.fetch(prev_tx, testnet=True)

    # create Tx_in, and assume we have one output
    tx_in = TxIn(bytes.fromhex(prev_tx), prev_index)

    change_amount = prev_amount - pay_amount - fee
    change_h160 = decode_base58(my_addr)
    change_script = p2pkh_script(change_h160)
    change_output = TxOut(change_amount, change_script)

    target_address = 'n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93' # Alice
    target_h160 = decode_base58(target_address)
    target_script = p2pkh_script(target_h160)
    target_output = TxOut(pay_amount, target_script)

    tx_out = [change_output, target_output]

    tx_obj = Tx(1, [tx_in], tx_out, 0, testnet=True)
    tx_obj.sign_input(0, private_key)
    # print(tx_obj.sign_input(0, private_key))
    print(tx_obj.serialize().hex())
    # rpc_connection.sendrawtransaction(tx_obj.serialize().hex())
    # headers = {'content-type': 'application/x-www-form-urlencoded'}
    # tx_raw = tx_obj.serialize().hex()
    # # payload_dict = {'key1': ['value1', 'value2']}
    # tx = requests.post(
    #     'https://api.blockcypher.com/v1/btc/test3/txs/push',
    #     headers=headers,
    #     data='{"tx": "%s"}' % tx_raw
    # )