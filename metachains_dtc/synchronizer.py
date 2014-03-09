class Synchronizer(object):
    """Synchronizer accesses data from and to a blockchain.

    Synchronizer must be instantiated with three objects:

    coin           -- An object that responds to blocks() and transactions(block)
    cloud          -- An object that responds to data_dump(bytes) and data_load(data, txid)
    starting_point -- Starting block index. Blockchain will be scanned from this point forward

    """
    def __init__(self, coin, cloud, starting_point):
        self.coin           = coin
        self.cloud          = cloud
        self.starting_point = starting_point

    def scan_database(self):
        """Scan database for non published data."""
        while True:
            payload = self.cloud.data_dump(self.coin.MaxPayloadSize)
            if payload is None:
                return

            self.process_database(payload)

    def scan_blockchain(self):
        """Scan blockchain for non registered data."""
        for block in self.coin.blocks(self.starting_point):
            for txid, data in self.coin.transactions(block):
                try:
                    self.process_blockchain(txid, info)
                except:
                    pass

    def process_blockchain(self, txid, info):
        """Load payload into local database."""
        self.cloud.data_load(info, txid)

    def process_database(self, payload):
        """Publish payload into blockchain."""
        self.coin.send_data(payload)
