#!/usr/bin/env python

import unittest
from flosrv import FlorinCoinSrv
from metachains import Florincoin, Synchronizer
from decimal import Decimal
import os


class MockCoin(object):
    @property
    def MaxPayloadSize(self): return 16

    def block_count(self):
        return 128

    def blocks(self, num):
        sample_block = {'height': 9999, }
        return [ sample_block ] * 5

    def send_data_address(self, payload, addr, amount):
        pass

    def transactions(self, block):
        return {}

class MockCloud(object):
    def __init__(self):
        self.i = 1

    def last_known_block(self):
        return 0

    def visit_block(self, blocknum):
        pass

    def data_load(self, txid):
        pass

    def data_dump(self, max_):
        self.i -= 1
        if self.i <= 0:
            return None
        else:
            return b'PAYLOAD' * 32

class FlorincoinTest(unittest.TestCase):
    DATA_SIZE = 2*1024

    def setUp(self):
        FlorinCoinSrv.Blocks = { hash(i): { 'address': 0, 'amount': 0, 'tx-comment': '-', 'tx': [], 'height': i, 'hash': hash(i), } for i in range(10) }
        self.srv = FlorinCoinSrv()
        self.flo = Florincoin(self.srv.url, self.srv.username, self.srv.passwd)
        self.sync = Synchronizer(self.flo, MockCloud())

    def tearDown(self):
        del self.flo
        del self.srv

    def test_misc(self):
        '''Check various jsonrpc queries
        '''
        block_count = self.flo.block_count()
        assert block_count
        response = self.flo.balance()
        assert response
        response = list(self.flo.blocks(0, block_count))
        assert len(response) == block_count

        response = self.flo.address(0)
        assert response

    def test_transactions(self):
        invalid_block = {
            'tx': 0,
        }
        response = self.flo.transactions(invalid_block)
        assert response

    def test_send(self):
        '''Test 'sendtoaddress' method used to store metadata
        '''
        large_data_corpus = b'i' * (FlorincoinTest.DATA_SIZE)
        response = self.flo.send_data_address(large_data_corpus, 'addr', Decimal('0.01'))
        assert response

    @unittest.skip('unrealistic test case')
    def test_send_high_entropy(self):
        high_entropy = os.urandom(FlorincoinTest.DATA_SIZE)
        response = self.flo.send_data_address(high_entropy, 'addr', Decimal('0.01'))
        assert response

    def test_roundtrip(self):
        large_data_corpus = b'R' * (FlorincoinTest.DATA_SIZE)
        response = self.flo.send_data_address(large_data_corpus, 'addr', Decimal('0.01'))
        assert response

#       self.sync.scan_database()
        self.sync.scan_blockchain()

class SyncTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_scan(self):
        coin = MockCoin()
        cloud = MockCloud()
        sync = Synchronizer(coin, cloud)
        sync.scan_database()
        assert cloud.i == 0
        sync.scan_blockchain()
