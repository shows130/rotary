# TCP server example
import sys
import socket
import logging
from utils import calc_checksum

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger('server')


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind(("", 5090))
server_socket.listen(5)

print("TCPServer Waiting for client on port 5090")

while True:
    client_socket, address = server_socket.accept()
    logger.info(f"I got a connection from {address}")
    while True:
        try:
            data = client_socket.recv(512)
            logger.info(f'received: {data}')
            if 22 != len(data):
                raise ValueError(f'data is not expected size (22), but {len(data)}')
            checksum = calc_checksum(data[1:20])
            if data[20].to_bytes(1, 'big') != checksum:
                raise ValueError('checksum error.')
        except Exception as e:
            logger.error(str(e))
        finally:
            client_socket.close()
            break
