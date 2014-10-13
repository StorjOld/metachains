import time
import json
import base64
import requests
import bz2 as compressor
import io
import codecs

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
        import binascii

        for txid in block["tx"]:
            entry = self._get_transaction(txid)
            try:
                fragment_entry = json.loads(entry['tx-comment'])
                region = codecs.encode(str(fragment_entry['region']), 'utf-8')
                fragment_entry['region'] = compressor.decompress(base64.b64decode(region))

            except (ValueError, IOError, TypeError, KeyError) as e:
                continue

            yield txid, fragment_entry

    def send_data_address(self, data, address, amount):
        """Send data to the blockchain via a standard transaction, or spanning
           transactions, if necessary.
        """

        # This routine ends up effectively doing json-over-json-over-json --
        #   we may need to consider revising it in order to be saner and fit better 
        single_block_space = Florincoin.MaxPayloadSize - Florincoin.ENCODING_OVERHEAD_ESTIMATE
        offset = 0
        i = 0
        prev_txid = None
        first_txid = None
        while offset < len(data):
            end = min(len(data), offset + single_block_space)
            region = data[offset:end]
            entry = {'prev_txid': prev_txid, 'region': codecs.decode(base64.b64encode(compressor.compress(region)), 'utf-8'), }
            if not prev_txid:
                entry['total_length'] = len(data)
            if first_txid:
                entry['first_txid'] = first_txid

            entry['index'] = i
            txid = self.jsonrpc("sendtoaddress", [address, float(amount), "storj", "storj", json.dumps(entry)])

            if not first_txid:
                first_txid = txid
            prev_txid = txid
            offset += len(region)
            i += 1

        return first_txid
