#!/usr/bin/env python

import unittest
from flosrv import FlorinCoinSrv
from metachains import Florincoin
from decimal import Decimal

class FlorincoinTest(unittest.TestCase):
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

    def test_send(self):
        '''Test 'sendtoaddress' method used to store metadata
        '''
        DATA_SIZE = 2*1024
        large_data_corpus = b'i' * (DATA_SIZE)
        response = self.flo.send_data_address(large_data_corpus, 'addr', Decimal('0.01'))
        assert response
        for item in response:
#           print('item', item)
            pass
