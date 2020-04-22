

def UTXO_output():
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
    return prev_tx, prev_index