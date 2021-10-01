# TCP server example
import sys          
import socket
import logging
from utils import calc_checksum

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)         #로그 기본 설정(초기시작문자, 단계)
logger = logging.getLogger('server')                                #'server'의 로그를 받아온다


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #소켓 생성(주소 패밀리, 소켓 유형) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #소켓기본 설정

server_socket.bind(("", 5090))  #소켓 주소 정보 할당(ip,port)
server_socket.listen(5)         #연결 수신 대기 : 최대 5개까지 

print("TCPServer Waiting for client on port 5090")

while True:
    client_socket, address = server_socket.accept()         #client소켓과 주소를 튜플로 받아온다
    logger.info(f"I got a connection from {address}")       #info level의 log출력
    while True:
        try:
            data = client_socket.recv(512)                  #0.5kb까지 소켓통신을 통해 받아온다
            logger.info(f'received: {data}')                #log를 통해 받은 data를 출력
            #data의 길이가 22가 아닐경우 오류 알림
            if 22 != len(data):
                raise ValueError(f'data is not expected size (22), but {len(data)}')
            #변조 확인 : data를 계산
            checksum = calc_checksum(data[1:20])
            #수신된 data내부의 변조확인항과 계산한 변조확인항을 비교
            #변조확인 결과가 같지 않을 경우 예외 발생
            if data[20].to_bytes(1, 'big') != checksum:
                raise ValueError('checksum error.')         #값의 형태는 에러가 아니나 원하는 값이 아닐 경우 사용하는 에러 발생 코드 
        except Exception as e:
            logger.error(str(e))            #error level의 log출력
        finally:
            client_socket.close()           #client socket을 닫는다
            break
