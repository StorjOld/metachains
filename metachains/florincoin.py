import time
import json
import base64
import requests
import bz2 as compressor

class Florincoin(object):
    """Florincoin abstracts away all RPC specific methods."""

    MaxPayloadSize = 528
    ENCODING_OVERHEAD_ESTIMATE = 196

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def jsonrpc(self, method, params):
        """Execute a json rpc method (with delayed retries)."""
        while True:
            try:
                response = requests.post(
                    self.url,
                    headers = {'Content-Type': 'text/plain'},
                    data = json.dumps({
                        "jsonrpc": "2.0",
                        "id": 42,
                        "method": method,
                        "params": params }),
                    auth = requests.auth.HTTPBasicAuth(self.username, self.password))

                return json.loads(response.text)["result"]
            except requests.exceptions.ConnectionError:
                time.sleep(2.0)
                continue


    def block_count(self):
        """Return the total number of blocks."""
        return self.jsonrpc("getblockcount", [])

    def balance(self):
        """Return the total balance."""
        return self.jsonrpc("getbalance", [])

    def address(self, account):
        return self.jsonrpc("getaccountaddress", [account])

    def blocks(self, index = 0, count=-1):
        """Return blocks from blockchain.

        Arguments:
        index -- starting index (0 based).
        count -- number of blocks to yield.

        """
        last = self.block_count() if count < 0 else index + count
        for i in range(index, last):
            yield self.jsonrpc("getblock", [self.jsonrpc("getblockhash", [i])])


    def _get_transaction(self, txid):
        return self.jsonrpc('decoderawtransaction', [ self.jsonrpc("getrawtransaction", [txid])])

    def transactions(self, block):
        """Return transaction identifier and data."""
        for txid in block["tx"]:
            entry = self._get_transaction(txid)
            try:
                fragment = compressor.decompress(base64.b64decode(entry['tx-comment']))
            except (IOError, TypeError) as e:
                continue
            yield txid, fragment

    def send_data_address(self, data, address, amount):
        """Send data to the blockchain via a standard transaction, or spanning
           transactions, if necessary.
        """

        # This routine ends up effectively doing json-over-json-over-json --
        #   we may need to consider revising it in order to be saner and fit better 
        single_block_space = Florincoin.MaxPayloadSize - Florincoin.ENCODING_OVERHEAD_ESTIMATE
        accum = []
        offset = 0
        i = 0
        prev_txid = None
        first_txid = None
        while offset < len(data):
            end = min(len(data), offset + single_block_space)
            region = data[offset:end]
            entry = {'prev_txid': prev_txid, 'region': str(base64.b64encode(compressor.compress(region))), }
            if not prev_txid:
                entry['total_length'] = len(data)
                entry['first_txid'] = first_txid

            entry['index'] = i
            txid = self.jsonrpc("sendtoaddress", [address, float(amount), "storj", "storj", json.dumps(entry)])
            if not first_txid:
                first_txid = txid
            accum.append(txid)
            prev_txid = txid
            offset += len(region)
            i += 1

        return accum
