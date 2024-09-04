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

class ChatRoom:
    def __init__(self, name) -> None:
        self.name: str = ''
        # self.password: str = ''
        self.tokenList: list[str] = []

user_dict: dict[str, list] = {}

class Tcp_Server:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001

    # 接続受け付け
    def listen(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
        self.sock.listen(1)


    # データ送信
    def send(self, data: bytes, host: str, port: int) -> None:
        return 0

    # トークン作成
    def createToken(self) -> int:
        return secrets.token_hex(16)


    def communication(self) -> None:
        self.listen()

        while True:
            # 型ヒント
            connection: socket.socket
            address: tuple[str, int]

            connection, address = self.sock.accept()

            data: bytes = connection.recv(4096)

            header:bytes = data[:32]
            body:bytes = data[32:]
            roomNameSize: int = int.from_bytes(header[0], 'big')
            operation: int = int.from_bytes(header[1], 'big')
            state: int = int.from_bytes(header[2], 'big')
            roomName: str = body[:roomNameSize].decode('utf-8')
            username: str = body[roomNameSize:].decode('utf-8')

            if operation == 1:
                state = 1
                state_bytes = state.to_bytes(1, 'big')
                connection.send(header[0] + header[1] + state_bytes + header[3:] + body)
                








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
