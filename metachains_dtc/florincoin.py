import time
import json
import base64
import requests

class Florincoin(object):
    """Florincoin abstracts away all RPC specific methods."""

    MaxPayloadSize = 528

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
#               continue
                raise


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

    def transactions(self, block):
        """Return transaction identifier and data."""
        for txid in block["tx"]:
            rawdata = self.jsonrpc("getdata", [txid])
            if rawdata is None:
                continue

            yield txid, base64.b64decode(rawdata)

    def send_data_address(self, data, address, amount):
        """Send data to the blockchain via a standard transaction."""

        if len(data) > Florincoin.MaxPayloadSize:
            raise Exception('not handled yet')
        return self.jsonrpc("sendtoaddress", [address, str(amount), "storj", "storj", str(base64.b64encode(data))])
