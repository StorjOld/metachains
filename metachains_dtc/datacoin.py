import time
import json
import base64
import requests

class Datacoin(object):
    """Datacoin abstracts away all RPC specific methods."""

    MaxPayloadSize = 128*1024

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def jsonrpc(self, method, params):
        """Execute a json rpc method (with delayed retries)."""
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
        except requests.exceptions.ConnectionError:
            time.sleep(2.0)
            return self.jsonrpc(method, params)

        return json.loads(response.text)["result"]

    def block_count(self):
        """Return the total number of blocks."""
        return self.jsonrpc("getblockcount", [])

    def blocks(self, index = 0, count=-1):
        """Return blocks from blockchain.

        Arguments:
        index -- starting index (0 based).
        count -- number of blocks to yield.

        """
        last = self.block_count() if count < 0 else index + count
        for i in xrange(index, last):
            yield self.jsonrpc("getblock", [self.jsonrpc("getblockhash", [i])])

    def transactions(self, block):
        """Return transaction identifier and data."""
        for txid in block["tx"]:
            rawdata = self.jsonrpc("getdata", [txid])
            if rawdata is None:
                continue

            yield txid, base64.decode(rawdata)

    def send_data(self, data):
        """Send data to the blockchain."""
        return self.jsonrpc("senddata", [base64.b64encode(data)])
