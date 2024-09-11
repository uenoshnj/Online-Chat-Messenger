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


class User:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.token: str = ''
        self.address: tuple[str, int]


user_dict: dict[str, list] = {}

class TcpServer:
    def __init__(self) -> None:
        
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001
        self.header_buff: int = 32
        self.payload_buff: int = 37

    # 接続受け付け
    def listen(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
        self.sock.listen(1)

    # データ送信
    def send(self, data: bytes, host: str, port: int) -> None:
        return 0

    # トークン作成
    def create_token(self) -> str:
        digit = random.randrange(10, 128)
        return secrets.token_hex(digit)

    # 応答ヘッダ作成
    def set_response(self, roomname_size: int, operation: int, payload_size: int) -> bytes:
        return protocol.create_header(roomname_size, operation, 1, payload_size)

    # ルーム作成
    def operation(self, connection: socket.socket, operation: int, data:bytes) -> None:
        roomname_size: int = protocol.get_roomname_size(header)
        operation: int = protocol.get_operation(header)
        state: int = protocol.get_state(header)
        roomname: str = protocol.get_roomname(body, roomname_size)
        username: str = protocol.get_payload(body, roomname_size)

        connection.send(self.set_response(roomname_size, operation, len(username)))

        if operation == 1:
            state_bytes: bytes = (1).to_bytes(1, 'big')
            connection.send(header[0] + header[1] + state_bytes + header[3:] + body)
            chat_room: ChatRoom = ChatRoom(roomname)
            chat_room.hostUser = username

            token: str = self.create_token()
            user: User = User(username)
            chat_room.token = token
            chat_room.user_list.append(user)

            # トークンをクライアントに送信
            connection.send()

        

    def communication(self) -> None:
        
        self.listen()

        while True:
            # 型ヒント
            connection: socket.socket
            address: tuple[str, int]

            connection, address = self.sock.accept()

            data: bytes = connection.recv(self.header_buff + self.payload_buff)

            header: bytes = data[:self.header_buff]
            body: bytes = data[self.header_buff:]

            roomname_size: int = int.from_bytes(header[0], 'big')
            operation: int = int.from_bytes(header[1], 'big')
            state: int = int.from_bytes(header[2], 'big')
            roomname: str = body[:roomname_size].decode('utf-8')
            username: str = body[roomname_size:].decode('utf-8')

            if operation == 1:
                state: int = 1
                state_bytes: bytes = state.to_bytes(1, 'big')
                connection.send(header[0] + header[1] + state_bytes + header[3:] + body)
                
                chatRoom: ChatRoom = ChatRoom(roomname)
                chatRoom.hostUser = username

                # トークン作成
                token: str = self.createToken()

                user: User = User(username)
                chatRoom.token = token
                chatRoom.user_list.append(user)


                connection.send()



class UdpServer:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001

        self.buffer: int = 4096
        self.user_dict: dict[str, tuple] = {}

    # ソケット紐づけ
    def set_bind(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
        print('Waiting for receive data.')
    
    # データ送信
    def send(self, sendData: bytes) -> None:
        for address in self.user_dict.values():
            self.sock.sendto(sendData, address)

    # データ受信
    def receive(self) -> bytes:
        return  self.sock.recvfrom(self.buffer)

    # ユーザの存在確認
    def is_exist_user(self, username: str) -> bool:
        return username in self.user_dict.keys()

    def communication(self) -> None:
        self.set_bind()
        try:
            while True:
                # 型ヒント
                receiveData: bytes
                address: tuple
                
                receiveData, address = self.receive()
                
                # バイトから文字列に変換
                usernamelen: int = int.from_bytes(receiveData[:1], 'big')
                username: str = receiveData[1:1 + usernamelen].decode('utf-8')
                msg: str = receiveData[1 + usernamelen:].decode('utf-8')
                
                if not self.is_exist_user(username):
                    self.user_dict[username] = address

                # タイムアウトユーザ、退出ユーザをリレーシステムから削除
                if msg == 'exit':
                    print(f"delete {username} from relay")
                    del self.user_dict[username]

                self.send(receiveData)
            
        finally:
            self.sock.close()

    

def main():

    udp_server_chat: UdpServer = UdpServer()
    udp_server_chat.communication()

main()
