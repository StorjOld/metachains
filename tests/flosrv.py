
from six.moves import (SimpleHTTPServer, BaseHTTPServer)
from threading import Thread
from six.moves import socketserver
import socket
import traceback
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
    Blocks = { }

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
            for bhash, block in FlorinCoinSrv.Blocks.items():
                if block['height'] == blocknum:
                    return block['hash']
            return None

        def handle_getblock(self, blockhash):
            return FlorinCoinSrv.Blocks[blockhash]

        def handle_getbalance(self):
            return str(FlorinCoinSrv.CURRENT_BAL)

        def handle_sendtoaddress(self, addr, amount, comment, comment_to, tx_comment):
            if len(tx_comment) > 528:
                raise FloSrvException('tx-comment too long: {}'.format(len(tx_comment)))
            txid = str(uuid.uuid1())
            other_txids = list(str(uuid.uuid1()) for i in range(7))
            blocknum = len(FlorinCoinSrv.Blocks)
            blockhash = str(uuid.uuid1())
            block = {  'size': 0,
                      'tx': [txid] + other_txids, 'height': blocknum, 'hash': blockhash,
                    }
            FlorinCoinSrv.Blocks[blockhash] = block

            return txid

        def handle_getblockcount(self):
            return len(FlorinCoinSrv.Blocks)

        def do_POST(self):
            try:
                result = self._handle_req()
                success = True
                response = {'result': result, }
            except (KeyError, AttributeError, IndexError, FloSrvException) as e:
                success = False
                response = {'result': None, 'errors': str(e), }
#               traceback.print_exc(e)
#               print('ERR:', str(e))
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
