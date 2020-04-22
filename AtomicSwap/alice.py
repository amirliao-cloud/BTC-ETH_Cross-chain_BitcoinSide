from helper.helper import hash160, decode_base58, little_endian_to_int, hash256, int_to_little_endian
from Scripts.Script import p2pkh_script, p2sh_script, atomic_swap_output_script
from Transaction.Tx import Tx, TxIn, TxOut
import requests
import json
from crypto.Signature import PrivateKey

from Transaction.Tx import TxFetcher
from AtomicSwap.bob import bob_addr_btc
import time
from AtomicSwap.util import broadcast_tx


alice_secret_atomic_swap = "thisIsASecretPassword123".encode('utf-8')
len_alice_secret = len(alice_secret_atomic_swap)
print("Alice's secret is: ", alice_secret_atomic_swap)
alice_secret = little_endian_to_int(hash256(b'Alice'))
alice_private_key = PrivateKey(secret=alice_secret)
alice_public_key = alice_private_key.point.sec()
alice_addr_btc = 'n4mNGWL1ycLk45xgvEEn8V2uKbnpa7wr93'

fee = int(0.00005 * 100000000)
pay_amount = int(0.001 * 100000000)
lock_time = 3600 + int(time.time())


alice_locktime = lock_time
bob_locktime = lock_time


def hash_of_secret():
    return hash160(alice_secret_atomic_swap)
# '853b775079232503df966e626618e1d388a95720'

def alice_swap_tx():
    prev_tx, prev_index, prev_amount, prev_output_script = None, None, None, None
    url_addr_history = '{}/addrs/{}/full'.format(TxFetcher.get_url(testnet=True), alice_addr_btc)
    response_addr_history = requests.get(url_addr_history)
    response_addr_history_binary = response_addr_history.content
    addr_history_json = json.loads(response_addr_history_binary)
    # since a tx has multiple outputs to cover the pay_amount, we only consider the output that has sufficient coins
    if addr_history_json['balance'] < pay_amount + fee:
        print('The balance of address %s is not enough to cover the payment', alice_addr_btc)
    for tx_info in addr_history_json['txs']:
        if prev_tx is not None:
            break
        for i, output in enumerate(tx_info['outputs']):
            if output['value'] >= pay_amount + fee and output['addresses'][0] == alice_addr_btc:
                prev_tx = tx_info['hash']
                prev_index = i
                prev_amount = output['value']
                break

    hash_secret = hash_of_secret()
    tx_in = TxIn(bytes.fromhex(prev_tx), prev_index)

    change_amount = prev_amount - pay_amount - fee
    change_h160 = decode_base58(alice_addr_btc)
    change_script = p2pkh_script(change_h160)
    change_output = TxOut(change_amount, change_script)

    target_address = bob_addr_btc
    target_h160 = decode_base58(target_address)
    target_output_script = atomic_swap_output_script(int_to_little_endian(len_alice_secret, 1), hash_secret, change_h160, target_h160, int_to_little_endian(alice_locktime, 4))
    target_output = TxOut(pay_amount, target_output_script)

    tx_out = [change_output, target_output]

    # tx_obj = Tx(1, [tx_in], tx_out, int(time.time()), testnet=True) # set nLocktime to present time
    tx_obj = Tx(1, [tx_in], tx_out, 0, testnet=True)  # set nLocktime to present time
    tx_obj.sign_input(0, alice_private_key)

    print('Alice swap tx (BTC) created successfully!, TX ID: ', tx_obj.id())
    return tx_obj


def alice_get_refund_tx(tx_id):
    tx_in = TxIn(bytes.fromhex(tx_id), 1) # note that here the output index of alice's transaction is 1
    target_address = alice_addr_btc
    target_h160 = decode_base58(target_address)
    target_output_script = p2pkh_script(target_h160)
    target_output = TxOut(pay_amount - fee - fee, target_output_script)

    tx_out = [target_output]

    tx_obj = Tx(1, [tx_in], tx_out, 0, testnet=True)  # set nLocktime to present time
    tx_obj.sign_input_atomic_swap_false_branch(alice_secret, 0, alice_private_key)
    print('Alice refund tx (BTC) created successfully!, TX ID: ', )
    return tx_obj


def is_expired(sleep_time):
    if sleep_time > lock_time:
        return True
    return False


# if __name__ == '__main__':
#     alice_swap_tx_id = '803c2292fd701f81f6d479842ffc4ac66845642cc42f7808d1fc088b1bc4ba1d'
#     tx = alice_get_refund_tx(alice_swap_tx_id)
#     broadcast_tx(tx)


#
if __name__ == '__main__':
#     #claim process
    tx_alice = alice_swap_tx()

    broadcast_tx(tx_alice)





