from bitcoinrpc.authproxy import AuthServiceProxy


def broadcast_tx(tx):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332" % ('abel', 'abel'), timeout=120)
    print(tx.serialize().hex())
    print(tx.id())
    rpc_connection.sendrawtransaction(tx.serialize().hex())
