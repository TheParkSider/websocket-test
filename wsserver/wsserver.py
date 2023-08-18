import threading
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from websocket_server import WebsocketServer

root = getLogger()
root.handlers = []

logger = getLogger(__name__)
logger.setLevel(DEBUG)

fmt_file = '[%(asctime)s] %(name)s %(levelname)s: %(message)s'
fmt_stream = '[%(asctime)s] %(name)s %(levelname)s: %(message)s'

fh = FileHandler('./mylog.log')
fh.setLevel(DEBUG)
fh.setFormatter(Formatter(fmt_file))
logger.addHandler(fh)

sh = StreamHandler()
sh.setLevel(INFO)
sh.setFormatter(Formatter(fmt_stream))
logger.addHandler(sh)

def hello():
    logger.info("Hello! This is wsserver.")

class WebServerRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info(f"received!")
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        message = "Hello, world!"
        self.wfile.write(bytes(message, "utf8"))
        return

class WebServer(ThreadingHTTPServer):
    def __init__(self, host, port):
        super().__init__((host, port), WebServerRequestHandler)
    
    def serve_forever(self, poll_interval: float = 0.5):
        logger.info(f"web starts listening")
        super().serve_forever(poll_interval)

    def run(self):
        threading.Thread(target=self.serve_forever).start()

class WsServer(WebsocketServer):
    def __init__(self, host, port, loglevel):
        super().__init__(host, port, loglevel)

    def on_new_client(self, client, server):
        logger.info(f"new client - id: {client['id']}")
        server.send_message_to_all("hey all, a new client has joined us")

    def on_client_left(self, client, _):
        if( client ):
            logger.info(f"client left - id: {client['id']}")

    def on_message_received(self, client, server, message):
        logger.info(f"client said - id: {client['id']}, message: {message}")
        server.send_message_to_all(f"Someone said: {message}")

    def run(self):
        logger.info(f"ws starts listening")
        self.set_fn_new_client(self.on_new_client)
        self.set_fn_client_left(self.on_client_left)
        self.set_fn_message_received(self.on_message_received)
        self.run_forever(threaded=True)

PORT = 9001
IP_ADDR = '127.0.0.1'

websv = WebServer(host=IP_ADDR, port=PORT)
websv.run()

wssv = WsServer(host=IP_ADDR, port=PORT+1, loglevel=DEBUG)
wssv.run()

input("Press a key to terminate server\n")
wssv.shutdown_gracefully()
websv.shutdown()