#!/usr/bin/env python

import unittest
from flosrv import FlorinCoinSrv
from metachains import Florincoin
from decimal import Decimal
import os

class FlorincoinTest(unittest.TestCase):
    DATA_SIZE = 2*1024

    def setUp(self):
        self.srv = FlorinCoinSrv()
        self.flo = Florincoin(self.srv.url, self.srv.username, self.srv.passwd)


    def tearDown(self):
        del self.flo
        del self.srv

    def test_misc(self):
        '''Check various jsonrpc queries
        '''
        response = self.flo.block_count()
        assert response
        response = self.flo.balance()
        assert response
        response = list(self.flo.blocks(0, 16))
        assert len(response) == 16

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
        for item in response:
            assert 'tx' in item

    @unittest.skip('unrealistic test case')
    def test_send_high_entropy(self):
        high_entropy = os.urandom(FlorincoinTest.DATA_SIZE)
        response = self.flo.send_data_address(high_entropy, 'addr', Decimal('0.01'))
        assert response
        for item in response:
            assert 'tx' in item
