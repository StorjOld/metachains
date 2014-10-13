
from decimal import Decimal
from collections import defaultdict
import operator
import logging

class Synchronizer(object):
    """Synchronizer accesses data from and to a blockchain.

    Synchronizer must be instantiated with three objects:

    coin           -- An object that responds to blocks() and transactions(block)
    cloud          -- An object that responds to data_dump(bytes) and data_load(data, txid)

    """
    ConfirmationThreshold = 10
    TransactionAmount = Decimal('0.05')
    TransactionAddress = "F94Vd1E6Hx2uhntGRo8mn3aJvQLS4KXmSA"

    def __init__(self, coin, cloud):
        self.coin           = coin
        self.cloud          = cloud
        self._log = logging.getLogger('storj.metachains')

    def scan_database(self):
        """Scan database for non published data."""
        while True:
            payload = self.cloud.data_dump(self.coin.MaxPayloadSize)
            if payload is None:
                return

            self._log.info('scan_database: processing payload')
            self.process_database(payload)

    def scan_blockchain(self):
        """Scan blockchain for non registered data, reassembling the 
           data regions.
        """
        outstanding_txns = {}
        for block in self.coin.blocks(self.cloud.last_known_block()):
            self._log.info('scan_blockchain: indexing block #{}'.format(block['height'])) # Todo make this debug
            for txid, entry in self.coin.transactions(block):
                if not txid:
                    continue
                outstanding_txns[txid] = (entry, block)

        linked_entries = defaultdict(list)
        heads = {}
        for txid, (entry, block) in outstanding_txns.items():
            if entry['prev_txid'] == None:
                heads[txid] = (entry, block)
            elif entry['prev_txid'] in outstanding_txns:
                linked_entries[entry['first_txid']].append(entry)

        def is_complete(txid):
            return heads[txid][0]['total_length'] == sum([len(entry['region']) for entry in linked_entries[txid]], len(heads[txid][0]['region']))

        lowest_incomplete_block = list(self.coin.blocks(self.coin.block_count() - 1))[-1]
        for txid, (head_entry, head_block) in heads.items():
            if not is_complete(txid):
                # The blockchain does not yet contain all constituent
                #   fragments for this entry
                if head_block['height'] < lowest_incomplete_block['height']:
                    lowest_incomplete_block = head_block
                continue

            tail = b''.join(entry['region'] for entry in sorted(linked_entries[txid], key=operator.itemgetter('index')))
            data = head_entry['region'] + tail
            try:
                self.process_blockchain(txid, data)
            except: #FIXME: this can't be what we want?
                pass

        self.confirm(lowest_incomplete_block) # FIXME off by one

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
