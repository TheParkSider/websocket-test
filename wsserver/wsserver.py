import time
from logging import getLogger, StreamHandler, FileHandler, Formatter, DEBUG, INFO
from websocket_server import WebsocketServer

root = getLogger()
root.handlers = []

logger = getLogger(__name__)
logger.setLevel(DEBUG)

fmt_file = '[%(asctime)s] %(name)s %(levelname)s: %(message)s'
fmt_stream = 'LOGGER [%(asctime)s] %(name)s %(levelname)s: %(message)s'

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

def on_new_client(client, server):
    logger.debug(f"new client - id: {client['id']}")
    server.send_message_to_all("hey all, a new client has joined us")

def on_client_left(client, _):
    if( client ):
        logger.debug(f"client left - id: {client['id']}")

def on_message_received(client, server, message):
    logger.debug(f"client said - id: {client['id']}, message: {message}")
    server.send_message_to_all(f"Someone said: {message}")

def run(sv):
    sv.set_fn_new_client(on_new_client)
    sv.set_fn_client_left(on_client_left)
    sv.set_fn_message_received(on_message_received) 
    sv.run_forever(threaded=True)

PORT = 9001
IP_ADDR = '127.0.0.1'
sv = WebsocketServer(host=IP_ADDR, port=PORT, loglevel=DEBUG)
run(sv)

input("Press a key to terminate server: ")
sv.shutdown_gracefully()