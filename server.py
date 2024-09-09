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

class ChatRoom:
    def __init__(self, name) -> None:
        self.name: str = ''
        # self.password: str = ''
        self.user_list: list[User] = []
        self.hostUser: str = ''
        self.token: str = ''



class User:
    def __init__(self, name: str) -> None:
        self.name = name


user_dict: dict[str, list] = {}

class Tcp_Server:
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
    def createToken(self) -> str:
        digit = random.randrange(10, 128)
        return secrets.token_hex(digit)


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
            roomNameSize: int = int.from_bytes(header[0], 'big')
            operation: int = int.from_bytes(header[1], 'big')
            state: int = int.from_bytes(header[2], 'big')
            roomName: str = body[:roomNameSize].decode('utf-8')
            username: str = body[roomNameSize:].decode('utf-8')

            if operation == 1:
                state: int = 1
                state_bytes: bytes = state.to_bytes(1, 'big')
                connection.send(header[0] + header[1] + state_bytes + header[3:] + body)
                
                chatRoom: ChatRoom = ChatRoom(roomName)
                chatRoom.hostUser = username

                # トークン作成
                token: str = self.createToken()

                user: User = User(username)
                chatRoom.token = token
                chatRoom.user_list.append(user)


                connection.send()









class Udp_Server:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001

        self.buffer: int = 4096
        self.user_dict: dict[str, tuple] = {}

    # ソケット紐づけ
    def setBind(self) -> None:
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
    def isExistUser(self, username: str) -> bool:
        return username in self.user_dict.keys()

    def communication(self) -> None:
        self.setBind()
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
                
                if not self.isExistUser(username):
                    self.user_dict[username] = address

                # タイムアウトユーザ、退出ユーザをリレーシステムから削除
                if msg == 'exit':
                    print(f"delete {username} from relay")
                    del self.user_dict[username]

                self.send(receiveData)
            
        finally:
            self.sock.close()

    

def main():

    udp_server_chat: Udp_Server = Udp_Server()
    udp_server_chat.communication()

main()
