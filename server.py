import socket
import threading
import secrets
import random

import protocol

class ChatRoom:
    def __init__(self, name) -> None:
        self.name: str = name
        # self.password: str = ''
        self.user_list: list[User] = []
        self.hostUser: str = ''

    def delete_user(self, token: str) -> None:
        for user in self.user_list:
            if user.token == token:
                self.user_list.remove(user)

room_list: list[ChatRoom] = []


class User:
    def __init__(self, name: str, token: str, address: tuple[str, int]) -> None:
        self.name: str = name
        self.token: str = token
        self.address: tuple[str, int] = address

class TcpServer:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001
        self.header_buff: int = 32
        self.payload_buff: int = 37
        self.ROOM_EXISTS_STATE: int = 3
        self.ROOM_NOT_EXISTS_STATE: int = 4
        self.USER_EXISTS_STATE: int = 5

    # 接続受け付け
    def listen(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
        self.sock.listen(1)
        print(f'[TCP] Waiting for connect...')

    # トークン作成
    def create_token(self) -> str:
        digit = random.randrange(10, 128)
        return secrets.token_hex(digit)
    
    # ルーム作成
    def _create_room(self, roomname: str, user: User) -> None:
        chat_room: ChatRoom = ChatRoom(roomname)
        chat_room.hostUser = user.name
        chat_room.user_list.append(user)
        room_list.append(chat_room)

    # ルーム存在チェック
    def _room_exists(self, roomname: str) -> bool | ChatRoom:
        for room in room_list:
            if room.name == roomname:
                return room

        return False


    # ルーム内でのユーザ名重複チェック
    def _username_exists(self, chat_room: ChatRoom, username: str) -> bool:
        for user in chat_room.user_list:
            if user.name == username:
                return True
        return False

    # 操作
    def _operation(self, connection: socket.socket, address: tuple[str, int],  data: bytes) -> int:
        operation: int = protocol.get_operation(data)
        roomname: str = protocol.get_roomname(data)
        username: str = protocol.get_payload(data)

        # 応答
        connection.send(protocol.create_header(operation, 1, roomname, username))

        if operation == 1:
            # 同一ルーム名の存在確認
            if self._room_exists(roomname):
                connection.send(protocol.create_header(operation, self.ROOM_EXISTS_STATE, roomname, username))
                return 1

            # トークン作成
            token: str = self.create_token()
            
            # ユーザ作成
            user: User = User(username, token, address)
            
            # ルーム作成
            self._create_room(roomname, user)
            
            # トークンをクライアントに送信
            connection.send(protocol.create_header(operation, 2, roomname, token) + protocol.create_body(roomname, token))

            return 0


        elif operation == 2:
            # ルーム名の存在確認し、存在しなければクライアントにルーム存在なしを返却
            chat_room: ChatRoom = self._room_exists(roomname)
            if chat_room:
                # トークン作成
                token: str = self.create_token()
                # ユーザ作成
                user: User = User(username, token, address)

            else:
                connection.send(protocol.create_header(operation, self.ROOM_NOT_EXISTS_STATE, roomname, username))
                return 1
            
            # ユーザの存在を確認し、存在している場合はクライアントにユーザ存在を返却
            if self._username_exists(chat_room, username):
                connection.send(protocol.create_header(operation, self.USER_EXISTS_STATE, roomname, username))
                return 1
            
            else:
                chat_room.user_list.append(user)
                connection.send(protocol.create_header(operation, 2, roomname, token) + protocol.create_body(roomname, token))


            return 0


    def communication(self) -> None:
        
        self.listen()

        while True:
            # 型ヒント
            connection: socket.socket
            address: tuple[str, int]

            connection, address = self.sock.accept()
            print(f'[TCP]connected by {address}')

            data: bytes = connection.recv(self.header_buff + self.payload_buff)

            self._operation(connection, address, data)


class UdpServer:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001

        self.buffer: int = 4096


    # ソケット紐づけ
    def _set_bind(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
    
    # データ送信
    def _send(self, send_data: bytes, room: ChatRoom) -> None:
        for user in room.user_list:
            self.sock.sendto(send_data, user.address)


    # データ受信
    def _receive(self) -> bytes:
        return  self.sock.recvfrom(self.buffer)

    # ルーム取得
    def _get_room(self, roomname: str) -> ChatRoom | bool:
        for room in room_list:
            if room.name == roomname:
                return room

        return False
    
    def _get_user(self, room: ChatRoom, token: str) -> User | bool:
        for user in room.user_list:
            if user.token == token:
                return user

        return False

    # ユーザトークン存在確認
    def _token_exists(self, token: str, room: ChatRoom) -> bool:
        for user in room.user_list:
            if user.token == token:
                return True

        return False

    def communication(self) -> None:
        self._set_bind()
        try:
            while True:
                # 型ヒント
                receive_data: bytes
                address: tuple
                
                receive_data, address = self._receive()
                
                # バイトから文字列に変換
                roomname: str = protocol.get_udp_roomname(receive_data)
                token: str = protocol.get_udp_token(receive_data)
                msg: str = protocol.get_message(receive_data)
                
                # ヘッダー作成
                header: bytes = protocol.create_udp_header(roomname, token)

                # ルーム名からユーザの参加中のルームを特定し、ルームの存在確認
                user_room: ChatRoom = self._get_room(roomname)
                if user_room == False:
                    body: bytes = protocol.create_udp_body(roomname, token, "room not exists!")
                    self.sock.sendto(header + body, address)
                    continue
                
                # トークンからユーザを特定し、ユーザの存在確認
                user: User = self._get_user(user_room, token)
                if user == False:
                    body: bytes = protocol.create_udp_body(roomname, token, "you're not join room")
                    self.sock.sendto(header + body, address)
                    continue

                # タイムアウトユーザ、退出ユーザをリレーシステムから削除、ホストユーザの場合はチャットルームも削除
                if msg == 'exit':
                    user_room.delete_user(token)
                    if user.name == user_room.hostUser:
                        room_list.remove(user_room)
                    continue

                msg = f'{user.name} : {msg}'

                body: bytes = protocol.create_udp_body(roomname, token, msg)
                self._send(header + body, user_room)

        finally:
            self.sock.close()

    

def main():
    tcp_server: TcpServer = TcpServer()
    udp_server: UdpServer = UdpServer()

    # tcp_server.communication()
    # udp_server.communication()

    thread_tcp: threading = threading.Thread(target=tcp_server.communication)
    thread_udp: threading = threading.Thread(target=udp_server.communication)

    thread_udp.start()
    thread_tcp.start()

    thread_udp.join()
    thread_tcp.join()
    
    
main()
