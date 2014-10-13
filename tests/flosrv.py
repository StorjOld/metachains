
from six.moves import (SimpleHTTPServer, BaseHTTPServer)
from threading import Thread
from six.moves import socketserver
import socket
import traceback
from decimal import Decimal
import base64
import cgi
import json
import codecs
import uuid
import io

class FloSrvException(Exception): pass

class FlorinCoinSrv(object):
    '''Acts as a JSONRPC server, simulating a Florincoin wallet/node
    '''

    PORT = 19929
    CURRENT_BAL = Decimal('10.0')
    Blocks = { }

    class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def __init__(self, request, client_addr, server):
            SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_addr, server)
            self.server = server

        def log_message(self, format, *args):
            pass

        def _handle_req(self):
            text = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
            req = json.loads(text)

            funcname = 'handle_' + req['method']
            req_handler = getattr(self, 'handle_' + req['method'])
            return req_handler(*req['params'])

        def handle_getaccountaddress(self, params):
            return 'addr'

        def handle_getblockhash(self, blocknum):
            for bhash, block in FlorinCoinSrv.Blocks.items():
                if block['height'] == blocknum:
                    return block['hash']
            return None

        def handle_decoderawtransaction(self, txraw):
            return json.loads(txraw)

        def handle_getrawtransaction(self, txid):
            tx_bytes = io.BytesIO(codecs.encode(json.dumps(self.server.Transactions[txid]), 'utf-8'))
            encoded = base64.b64encode(tx_bytes.getvalue())
            return json.dumps(self.server.Transactions[txid])

        def handle_getblock(self, blockhash):
            return FlorinCoinSrv.Blocks[blockhash]

        def handle_getbalance(self):
            return str(FlorinCoinSrv.CURRENT_BAL)

        def handle_sendtoaddress(self, addr, amount, comment, comment_to, tx_comment):
            if len(tx_comment) > 528:
                raise FloSrvException('tx-comment too long: {}'.format(len(tx_comment)))
            txid = str(hash(uuid.uuid1()))
            tx = { 'addr': addr, 'amount': amount, 'comment': comment, 'comment-to': comment_to,
                   'tx-comment': tx_comment,
                  }
            other_txids = list(str(uuid.uuid1()) for i in range(7))
            blocknum = len(FlorinCoinSrv.Blocks)
            blockhash = str(uuid.uuid1())
            block = {  'size': 0,
                      'tx': [txid] + other_txids, 'height': blocknum, 'hash': blockhash,
                    }
            FlorinCoinSrv.Blocks[blockhash] = block
            self.server.Transactions[txid] = tx
            filler_tx = { 'addr': 'filler', 'amount': 3.33, 'comment': 'filler', 'comment-to': 'filler',
                   'tx-comment': 'filler',
                  }
            for txid_ in other_txids:
                self.server.Transactions[txid_] = filler_tx

            return txid

        def handle_getblockcount(self):
            return len(FlorinCoinSrv.Blocks)

        def do_POST(self):
            try:
                result = self._handle_req()
                success = True
                response = {'result': result, }
            except (TypeError, KeyError, AttributeError, IndexError, FloSrvException) as e:
                success = False
                response = {'result': None, 'errors': str(e), }
            self.send_response(200 if success else 500)
            self.end_headers()
            self.wfile.write(codecs.encode(json.dumps(response), ('utf-8')))

        def do_GET(self):
            self.send_response(500)
            self.end_headers()

    
    class AnHTTPServer(BaseHTTPServer.HTTPServer):
        def __init__(self, *args, **kw):
            BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
            self.allow_reuse_address = True
            self.Transactions = {}

    def __init__(self):
        self.httpd = FlorinCoinSrv.AnHTTPServer(("", FlorinCoinSrv.PORT), FlorinCoinSrv.Handler)
        self.httpd_thread = Thread(target=self.httpd.serve_forever, group=None)
        self.httpd_thread.start()


    def __del__(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        del self.httpd
        self.httpd_thread.join()
        del self.httpd_thread

    @property
    def url(self):
        return u'http://localhost:{}'.format(FlorinCoinSrv.PORT)

    @property
    def username(self):
        return 'user'

    @property
    def passwd(self):
        return 'pass'
