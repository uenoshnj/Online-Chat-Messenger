
# データをバイトに変換
def create_header(roomname_size: int, operation: int, state: int, payload_size: int) -> bytes:
    return roomname_size.to_bytes(1, 'big') + operation.to_bytes(1, 'big') + state.to_bytes(1, 'big') + payload_size.to_bytes(29, 'big')

def create_body(roomname: str, payload: str) -> bytes:
    return roomname.encode('utf-8') + payload.encode('utf-8')

# バイトデータを変換
def get_roomname_size(header: bytes) -> int:
    return int.from_bytes(header[0], 'big')

def get_operation(header: bytes) -> int:
    return int.from_bytes(header[1], 'big')

def get_state(header: bytes) -> int:
    return int.from_bytes(header[2], 'big')

def get_payload_size(header: bytes) -> int:
    return int.from_bytes(header[3:], 'big')

def get_roomname(body: bytes, roomname_size: int) -> str:
    return body[:roomname_size].decode('utf-8')

def get_payload(body: bytes, roomname_size: int) -> str:
    return body[roomname_size:].decode('utf-8')