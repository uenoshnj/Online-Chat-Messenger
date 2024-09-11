
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
    return int.from_bytes(header[0], 'big')

def get_operation(data: bytes) -> int:
    header: bytes = _get_header(data)
    return int.from_bytes(header[1], 'big')

def get_state(data: bytes) -> int:
    header: bytes = _get_header(data)
    return int.from_bytes(header[2], 'big')

def get_payload_size(data: bytes) -> int:
    header: bytes = _get_header(data)
    return int.from_bytes(header[3:], 'big')

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