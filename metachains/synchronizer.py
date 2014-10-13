
from decimal import Decimal

class Synchronizer(object):
    """Synchronizer accesses data from and to a blockchain.

    Synchronizer must be instantiated with three objects:

    coin           -- An object that responds to blocks() and transactions(block)
    cloud          -- An object that responds to data_dump(bytes) and data_load(data, txid)

    """
    ConfirmationThreshold = 10
    TransactionAmount = Decimal('0.05')
    TransactionAddress = "FFPHkg8Z7ptMootRmGG19dtZJTYajmxWVz"

    def __init__(self, coin, cloud):
        self.coin           = coin
        self.cloud          = cloud

    def scan_database(self):
        """Scan database for non published data."""
        while True:
            payload = self.cloud.data_dump(self.coin.MaxPayloadSize)
            if payload is None:
                return

            self.process_database(payload)

    def scan_blockchain(self):
        """Scan blockchain for non registered data."""
        for block in self.coin.blocks(self.cloud.last_known_block()):
            for txid, data in self.coin.transactions(block):
                try:
                    self.process_blockchain(txid, data)
                except:
                    pass

            self.confirm(block)

    def process_blockchain(self, txid, info):
        """Load payload into local database."""
        self.cloud.data_load(info, txid)

    def process_database(self, payload):
        """Publish payload into blockchain."""
        self.coin.send_data_address(
            payload,
            self.TransactionAddress,
            self.TransactionAmount)

    def confirm(self, block):
        self.cloud.visit_block(
            max(block["height"] - self.ConfirmationThreshold, 0))
