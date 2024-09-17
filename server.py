'''
# オンラインチャットプログラム（サーバ）
    ・概要
    クライアントからのメッセージを待ち受ける

    ・プロトコル
    ヘッダー : ユーザ名の長さ（1バイト）+ メッセージの長さ（4バイト）
    データ : メッセージ本文
'''

import os
import socket
import sys
import time
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

    # ルームへユーザを追加
    def _add_to_room(self, roomname: str, user: User) -> bool:
        for room in room_list:
            if room.name == roomname:
                room.user_list.append(user)
                return True
        
        return False

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
                connection.send(protocol.create_header(operation, 2, roomname, token) + protocol.create_body(roomname, token))

            return 0

    # クライアントと通信
    def communication(self) -> None:
        
        self.listen()

        while True:
            # 型ヒント
            connection: socket.socket
            address: tuple[str, int]

            connection, address = self.sock.accept()
            print(f'connected by {address}')

            data: bytes = connection.recv(self.header_buff + self.payload_buff)

            self._operation(connection, address, data)
            


# class UdpServer:
#     def __init__(self) -> None:
#         self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.serverHost: str = '0.0.0.0'
#         self.serverPort: int = 9001

#         self.buffer: int = 4096
#         self.user_dict: dict[str, tuple] = {}

#     # ソケット紐づけ
#     def set_bind(self) -> None:
#         self.sock.bind((self.serverHost, self.serverPort))
#         print('Waiting for receive data.')
    
#     # データ送信
#     def send(self, sendData: bytes) -> None:
#         for address in self.user_dict.values():
#             self.sock.sendto(sendData, address)

#     # データ受信
#     def receive(self) -> bytes:
#         return  self.sock.recvfrom(self.buffer)

#     # ユーザの存在確認
#     def is_exist_user(self, username: str) -> bool:
#         return username in self.user_dict.keys()

#     def communication(self) -> None:
#         self.set_bind()
#         try:
#             while True:
#                 # 型ヒント
#                 receiveData: bytes
#                 address: tuple
                
#                 receiveData, address = self.receive()
                
#                 # バイトから文字列に変換
#                 usernamelen: int = int.from_bytes(receiveData[:1], 'big')
#                 username: str = receiveData[1:1 + usernamelen].decode('utf-8')
#                 msg: str = receiveData[1 + usernamelen:].decode('utf-8')
                
#                 if not self.is_exist_user(username):
#                     self.user_dict[username] = address

#                 # タイムアウトユーザ、退出ユーザをリレーシステムから削除
#                 if msg == 'exit':
#                     print(f"delete {username} from relay")
#                     del self.user_dict[username]

#                 self.send(receiveData)
            
#         finally:
#             self.sock.close()

    

def main():
    tcp_server: TcpServer = TcpServer()
    tcp_server.communication()
    
main()
