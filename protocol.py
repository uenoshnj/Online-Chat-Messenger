
# TCPプロトコル
# データをバイトに変換
def create_header(operation: int, state: int, roomname: str, payload: str) -> bytes:
    roomname_size = _get_roomname_size(roomname)
    payload_size = _get_payload_size(payload)
    return roomname_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + payload_size.to_bytes(29, 'big')

def create_body(roomname: str, payload: str) -> bytes:
    return roomname.encode('utf-8') + payload.encode('utf-8')

def _get_roomname_size(roomname: str) -> int:
    return len(roomname.encode('utf-8'))

def _get_payload_size(payload: str) -> int:
    return len(payload.encode('utf-8'))

# バイトデータを変換
def _get_header(data: bytes) -> bytes:
    return data[:32]

def _get_body(data: bytes) -> bytes:
    return data[32:]

def get_roomname_size(data: bytes) -> int:
    header: bytes = _get_header(data)
    return header[0]

def get_operation(data: bytes) -> int:
    header: bytes = _get_header(data)
    return header[1]

def get_state(data: bytes) -> int:
    header: bytes = _get_header(data)
    return header[2]

def get_payload_size(data: bytes) -> int:
    header: bytes = _get_header(data)
    return header[3:]

def get_roomname(data: bytes) -> str:
    header: bytes = _get_header(data)
    body: bytes = _get_body(data)
    roomname_size: int = get_roomname_size(header)
    return body[:roomname_size].decode('utf-8')

def get_payload(data: bytes) -> str:
    header: bytes = _get_header(data)
    body: bytes = _get_body(data)
    roomname_size: int = get_roomname_size(header)
    return body[roomname_size:].decode('utf-8')


# UDPプロトコル
# データをバイトに変換
def create_udp_header(roomname: str, token: str) -> bytes:
    roomname_size = _get_roomname_size(roomname)
    token_size = _get_token_size(token)
    return roomname_size.to_bytes(1, 'big') + token_size.to_bytes(1, 'big')

def create_udp_body(roomname: str, token: str, payload: str) -> bytes:
    return roomname.encode('utf-8') + token.encode('utf-8') + payload.encode('utf-8')

# バイトデータを変換
def _get_token_size(token: str) -> int:
    return len(token.encode('utf-8'))

def _get_udp_header(data: bytes) -> bytes:
    return data[:2]

def _get_udp_body(data: bytes) -> bytes:
    return data[2:]
    
def get_udp_roomname_size(data: bytes) -> int:
    header: bytes = _get_udp_header(data)
    return header[0]
    
def get_udp_token_size(data: bytes) -> int:
    header: bytes = _get_udp_header(data)
    return header[1]

def get_udp_roomname(data: bytes) -> str:
    header: bytes = _get_udp_header(data)
    body: bytes = _get_udp_body(data)
    roomname_size: int = get_udp_roomname_size(header)
    return body[:roomname_size].decode('utf-8')

def get_udp_token(data: bytes) -> str:
    header: bytes = _get_udp_header(data)
    body: bytes = _get_udp_body(data)
    roomname_size: int = get_udp_roomname_size(header)
    token_size: int = get_udp_token_size(header)
    return body[roomname_size:roomname_size+token_size].decode('utf-8')

def get_message(data: bytes) -> str:
    header: bytes = _get_udp_header(data)
    body: bytes = _get_udp_body(data)
    roomname_size: int = get_udp_roomname_size(header)
    token_size: int = get_udp_token_size(header)
    return body[roomname_size+token_size:].decode('utf-8')