def calc_checksum(data):
    checksum = sum(data) % 256
    checksum = checksum.to_bytes(1, byteorder='big')
    return checksum


def get_protocol_data(dt, data):
    # data = b'2103011012349999999'
    header = b'\x02'
    tail = b'\x03'
    data = bytes(f'{dt}{data}', 'utf-8')
    if len(data) != 19:
        raise ValueError(f'expected length is 19 but {len(data)}')
    checksum = sum(data) % 256
    checksum = checksum.to_bytes(1, byteorder='big')
    data = header + data + checksum + tail
    return data

    # print(calc_checksum(data[1:].decode()))

def calc_checksum(s):
    checksum = sum(s) % 256
    checksum = checksum.to_bytes(1, byteorder='big')
    return checksum