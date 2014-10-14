
from six.moves import (SimpleHTTPServer, BaseHTTPServer)
from threading import Thread
from six.moves import socketserver
import socket
from decimal import Decimal
import cgi
import json
import codecs
import uuid

class FloSrvException(Exception): pass

class FlorinCoinSrv(object):
    '''Acts as a JSONRPC server, simulating a Florincoin wallet/node
    '''

    PORT = 19929
    CURRENT_BAL = Decimal('10.0')
    BLOCK_COUNT = 1024
    FILLER_BLOCK = { 'address': 0, 'amount': 0, 'tx-comment': '-', 
                      'tx': 0, 'height': 0, 'hash': 0,
                    }
    Blocks = [FILLER_BLOCK] * BLOCK_COUNT

    class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _handle_req(self):
            text = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
            req = json.loads(text)

            return getattr(self, 'handle_' + req['method'])(*req['params'])

        def handle_getaccountaddress(self, params):
            return 'addr'

        def handle_getblockhash(self, blocknum):
            return FlorinCoinSrv.Blocks[blocknum]['hash']

        def handle_getblock(self, blockhash):
            some_block = { 'address': 0, 'amount': 0, 'tx-comment': '-', 
                      'tx': 0, 'height': 0, 'hash': 0,
                    }
            return some_block

        def handle_getbalance(self):
            return str(FlorinCoinSrv.CURRENT_BAL)

        def handle_sendtoaddress(self, addr, amount, comment, comment_to, tx_comment):
            if len(tx_comment) > 528:
                raise FloSrvException('tx-comment too long: {}'.format(len(tx_comment)))
            txid = str(uuid.uuid1())
            txid2 = str(uuid.uuid1())
            blocknum = 0
            block = {  'size': 0,
                      'tx': [txid, txid2], 'height': blocknum, 'hash': str(uuid.uuid1()),
                    }
            FlorinCoinSrv.Blocks.append(block)

            return block

        def handle_getblockcount(self):
            return FlorinCoinSrv.BLOCK_COUNT

        def do_POST(self):
            try:
                result = self._handle_req()
                success = True
                response = {'result': result, }
            except (KeyError, AttributeError, IndexError, FloSrvException) as e:
                success = False
                response = {'result': None, 'errors': str(e), }
            self.send_response(200 if success else 500)
            self.end_headers()
            self.wfile.write(codecs.encode(json.dumps(response), ('utf-8')))

        def do_GET(self):
            self.send_response(500)
            self.end_headers()

    
    class ReuseTCPServer(socketserver.TCPServer):
        def server_bind(self):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self.server_address)

    def __init__(self):
        self.httpd = FlorinCoinSrv.ReuseTCPServer(("", FlorinCoinSrv.PORT), FlorinCoinSrv.Handler)
        self.httpd_thread = Thread(target=self.httpd.serve_forever, group=None)
        self.httpd_thread.start()


    def __del__(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.httpd_thread.join()
        del self.httpd
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
