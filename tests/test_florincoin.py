#!/usr/bin/env python

import unittest
from flosrv import FlorinCoinSrv
from metachains_dtc import Florincoin
from decimal import Decimal

class FlorincoinTest(unittest.TestCase):
    def setUp(self):
        self.srv = FlorinCoinSrv()
        self.flo = Florincoin(self.srv.url, self.srv.username, self.srv.passwd)


    def tearDown(self):
        del self.flo
        del self.srv

    def test_misc(self):
        response = self.flo.block_count()
        print('block count', response)
        assert response
        response = self.flo.balance()
        assert response
        response = self.flo.blocks(0, 16)
        assert response

    def test_send(self):
        DATA_SIZE = 1024*1024 #1 meg
        large_data_corpus = b'i' * (DATA_SIZE)
        response = self.flo.send_data_address(large_data_corpus, 'addr', Decimal('0.01'))
        assert response
