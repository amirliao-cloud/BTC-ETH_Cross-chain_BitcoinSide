from helper.helper import hash160, decode_base58, little_endian_to_int, hash256
from Scripts.Script import p2pkh_script
from crypto.Signature import PrivateKey
from Transaction.Tx import Tx, TxIn, TxOut
from AtomicSwap.util import broadcast_tx
bob_secret = little_endian_to_int(hash256(b'Bob'))
bob_private_key = PrivateKey(secret=bob_secret)
alice_public_key = bob_private_key.point.sec()
bob_addr_btc = 'mtP5yN9q6bFdiWqwcDJsiobPBVVFdwQTvR'

fee = int(0.00005 * 100000000)
pay_amount = int(0.001 * 100000000)
alice_secret = "thisIsASecretPassword123".encode('utf-8')
len_alice_secret_atomic_swap = len(alice_secret)


def bob_redeem_tx(amount_to_send, alice_tx_id, alice_secret):
    txout_h160 = decode_base58(bob_addr_btc) # hash160 of the public key
    txout_script = p2pkh_script(txout_h160)
    tx_out = TxOut(amount_to_send, txout_script)

    tx_in = TxIn(bytes.fromhex(alice_tx_id), 1)
    tx_obj = Tx(1, [tx_in], [tx_out], 0, testnet=True)

    tx_obj.sign_input_atomic_swap_true_branch(alice_secret, 0, bob_private_key)
    if tx_obj.verify():
        print('Bob redeem from swap tx (BTC) created successfully!')
    return tx_obj


if __name__ == '__main__':
    alice_secret = "thisIsASecretPassword123".encode('utf-8')
    tx_alice_id = '59bf499c0bbce0489a0a9f4d2ed5c9521cb40a500c81212394fe86abed6e2b77'
    tx_bob_redeem = bob_redeem_tx(pay_amount - fee - fee, tx_alice_id, alice_secret)
    broadcast_tx(tx_bob_redeem)