# 변조확인항 계산
def calc_checksum(data):
    checksum = sum(data) % 256 #data값을 전부 더하고 256으로 나눈 나머지를 반환
    checksum = checksum.to_bytes(1, byteorder='big') #반환된 숫자를 1byte로 표현(읽는 방식 = 왼쪽부터)
    return checksum

def get_protocol_data(dt, data):
    # data = b'2103011012349999999'
    header = b'\x02' #프로토콜 시작을 알리는 항
    tail = b'\x03' #프로토콜 끝을 알리는 항
    data = bytes(f'{dt}{data}', 'utf-8') #시간과 각도값을 utf-8형식으로 바이트 형태로 인코딩
    #data의 길이가 19가 아닐경우 에러 문구 생성
    if len(data) != 19:
        raise ValueError(f'expected length is 19 but {len(data)}')
    #변조확인항 생성
    checksum = sum(data) % 256
    checksum = checksum.to_bytes(1, byteorder='big')

    #최종적으로 발신할 data 생성
    data = header + data + checksum + tail
    return data

    # print(calc_checksum(data[1:].decode()))

def calc_checksum(s):
    checksum = sum(s) % 256
    checksum = checksum.to_bytes(1, byteorder='big')
    return checksum