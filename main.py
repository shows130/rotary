import RPi.GPIO as GPIO
import time
import datetime
import socket
import argparse
import sqlite3
from functools import wraps
from contextlib import contextmanager

from rotary_encoder import Encoder
from utils import get_protocol_data


PIN_ENCODER_A = 16
PIN_ENCODER_B = 20

PIN_RESET_BUTTON = 18
PIN_ACTIVE_SIGNAL = 21

ACTIVATE_STATUS = 0

ENCODER = None

IP = 'localhost'
PORT = 5090
DB_FILE = 'pulse.db'

def reset_counter():
    pass


client_socket = None
def send_data_to_server(data):
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((IP, PORT))
        client_socket.send(data)
    except OSError as e:
        print(f'{e}: {IP} {PORT}')
        raise


def set_working_status(value):
    if GPIO.input(PIN_ACTIVE_SIGNAL):
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.000')
        ENCODER.value = 0
        ACTIVATE_STATUS = 1
    else:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.000')
        ACTIVATE_STATUS = 0
    print(f'{date} | {"activate" if ACTIVATE_STATUS else "deactivate"} | {ENCODER.value}')

    if not ACTIVATE_STATUS:
        dt = datetime.datetime.now().strftime('%y%m%d%H%M%S000')
        value = f'{abs(ENCODER.value):> 4d}'
        data = get_protocol_data(dt, value)
        print(data)

        try:
            send_data_to_server(data)
        except OSError as e:
            db_insert(dt, int(value))
            return

        # 연결이 가능한 상태일 경우 보내지 못한 데이터 전송 시도
        # 전송에 성공한 데이터는 삭제
        data = db_select()
        # data = [('210310151620000', 168), ('210310151625000', 356)]
        for dt, value in data:
            value = f'{value:> 4d}'
            data = get_protocol_data(dt, value)
            print(data)
            try:
                send_data_to_server(data)
                db_delete(dt)
            except OSError as e:
                return


def init():
    GPIO.setup(PIN_RESET_BUTTON, GPIO.IN)
    GPIO.add_event_detect(
        PIN_RESET_BUTTON, GPIO.FALLING,
        callback=reset_counter,
        bouncetime=50)

    GPIO.setup(PIN_ACTIVE_SIGNAL, GPIO.IN)
    GPIO.add_event_detect(
        PIN_ACTIVE_SIGNAL, GPIO.BOTH,
        callback=set_working_status,
        bouncetime=50)



def main():
    global ENCODER
    ENCODER = Encoder(PIN_ENCODER_A, PIN_ENCODER_B)
    init()
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()


@contextmanager
def db_context(db_file):
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    db_create(cur)
    yield cur
    con.commit()
    con.close()


def db_create(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS data  
    (datetime TEXT, pulse INTEGER)''')


def db_insert(dt, pulse):
    with db_context(DB_FILE) as cur:
        cur.execute(f'''INSERT INTO data VALUES('{dt}', {pulse})''')


def db_select(num=10):
    with db_context(DB_FILE) as cur:
        cur.execute(f'''SELECT * FROM data limit 10''')
        result = cur.fetchall()
    return result

def db_delete(dt):
    with db_context(DB_FILE) as cur:
        cur.execute(f'''DELETE FROM data WHERE datetime in ({dt})''')


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-a', '--host', default='localhost', type=str,
                       help='Server IP Address')
    parse.add_argument('-p', '--port', default=5090, type=int,
                       help='Server Port Number')

    parse.add_argument('--reset', action='store_true', help='DB Reset')
    parse.add_argument('--db-file', type=str, default='pulse.db',
                       help='DB File')

    arguments = parse.parse_args()
    IP = arguments.host
    PORT = arguments.port
    DB_FILE = arguments.db_file

    main()
