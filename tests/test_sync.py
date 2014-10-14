#!/usr/bin/env python

import unittest
from flosrv import FlorinCoinSrv
from metachains import Synchronizer
from decimal import Decimal
import os

class MockCoin(object):
    @property
    def MaxPayloadSize(self): return 16

    def blocks(self, num):
        sample_block = {'height': 9999, }
        return [ sample_block ] * 5

    def send_data_address(self, payload, addr, amount):
        pass

    def transactions(self, block):
        return {}

class MockCloud(object):
    def __init__(self):
        self.i = 10

    def last_known_block(self):
        return 11

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
