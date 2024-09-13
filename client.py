'''
# オンラインチャットプログラム（クライアント）
    ・概要
    サーバへ接続し、メッセージを送信する。

    ・プロトコル
    ヘッダー : ユーザ名の長さ（1バイト）
    データ : メッセージ本文
'''
import socket
import sys
import os
import threading
import time

import protocol

class TcpClient:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host: str = '0.0.0.0'
        self.server_port: int = 9001
        self.client_host: str = ''
        self.client_port: int = 0

        self.roomname: str = ''
        self.username: str = ''
        self.operation: int = 0
        self.state: int = 0
        self.ROOM_EXISTS_STATE: int = 3
        self.ROOM_NOT_EXISTS_STATE: int = 4
        self.USER_EXISTS_STATE: int = 5

    # 接続
    def connect(self) -> None:
        print(f'[TCP]Connect to {self.server_host}:{self.server_port}')
        try:
            self.sock.connect((self.server_host, self.server_port))
        
        except OSError as err:
            print(f'error : {err}')
            sys.exit(1)

    # 長さチェック
    def is_valid_length(self, input: str, length: int) -> bool:
        l: int = len(input)
        return 0 < l and l <= length

    # ルーム名の入力
    def _input_roomname(self) -> None:
        while not self.is_valid_length(self.roomname, 20):
            self.roomname = input('room name(Up to 20 characters) : ')

    # ユーザ名の入力
    def _input_username(self) -> None:
        while not self.is_valid_length(self.username, 10):
            self.username = input('user name(Up to 10 characters) : ')

    # 操作の入力
    def _input_operation(self) -> None:
        while self.operation != 1 and self.operation != 2:
            self.operation = int(input('input operation(1 or 2) : '))

    # サーバ初期化依頼
    def server_init(self, tcrp: bytes) -> None:
        try:
            self.sock.sendto(tcrp, (self.server_host, self.server_port))
        
        except OSError as e:
            print(f'error: {e}')

    # データ受信
    def receive(self) -> None:
        self.sock.recv()

    # ステートチェック
    def _check_state(self, data: bytes) -> None:
        state = protocol.get_state(data)
        
        # 作成するルームが存在する場合
        if state == self.ROOM_EXISTS_STATE:
            print(f'[TCP]Room {protocol.get_roomname(data)} already exists, close connection')
            self.sock.close()
            sys.exit(1)

        # 参加対象のルームが存在しない場合
        if state == self.ROOM_NOT_EXISTS_STATE:
            print(f'[TCP]Room {protocol.get_roomname(data)} does not exist, close connection')
            self.sock.close()
            sys.exit(1)
        
        # ユーザが既に存在する場合
        if state == self.USER_EXISTS_STATE:
            print(f'[TCP]Username:{protocol.get_payload(data)} already exist, close connection')
            self.sock.close()
            sys.exit(1)

    #
    def communication(self) -> None:
        # サーバへ接続
        self.connect()

        # ルーム名、ユーザ名、操作の入力
        self._input_roomname()
        self._input_username()
        self._input_operation()
        

        header: bytes = protocol.create_header(self.operation, self.state, self.roomname, self.username)
        body: bytes = protocol.create_body(self.roomname, self.username)
        tcpr: bytes = header + body

        self.server_init(tcpr)

        # 準拠
        data: bytes = self.sock.recv(32)
        if protocol.get_state(data) != 1:
            print(f'[TCP]Username:{protocol.get_payload(data)} is already exist, close the connection')
            self.sock.close()
            sys.exit(1)
        
        print(f'[TCP]server is processing. Wait for a minute...')

        # ルーム作成
        if self.operation == 1:
            # 完了
            data: bytes = self.sock.recv(4096)
            self._check_state(data)
            print(f'[TCP]{protocol.get_roomname(data)} created')

        # ルーム参加
        else :
            # 完了
            data: bytes = self.sock.recv(4096)
            self._check_state(data)
            print(f'[TCP]Joined {protocol.get_roomname(data)}')





# class UdpClient:
#     def __init__(self) -> None:
#         self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.serverHost: str = '0.0.0.0'
#         self.serverPort: int = 9001
#         self.clientHost: str = '127.0.0.1'
#         self.clientPort: int = 999999

#         self.username: str = ''
#         self.usernamelen: int = 0
#         self.buffer: int = 4096
#         self.lastSendTime: float = 0

#         self.faultCount: int = 0

#     # ソケット紐づけ
#     def set_bind(self) -> None:
#         self.sock.bind((self.clientHost, self.clientPort))
#         self.lastSendTime = time.perf_counter()

#     # データ送信
#     def send(self) -> None:
#         while True:    
#             message: str = input()
#             if self.check_timeout():
#                 message = 'exit'
#                 print('Time out!')
#             data: bytes = self.usernamelen.to_bytes(1, 'big') + f'{self.username}{message}'.encode('utf-8')
#             self.sock.sendto(data, (self.serverHost, self.serverPort))
#             self.lastSendTime = time.perf_counter()

#             if message == 'exit':
#                 self.sock.close()
#                 break

    
#     # データ受信
#     def receive(self) -> None:
#         while True:
#             data: bytes = self.sock.recv(self.buffer)
#             usernamelen = int.from_bytes(data[:1], 'big')
#             username = data[1:1+usernamelen].decode('utf-8')
#             message = data[1+usernamelen:].decode('utf-8')

#             if message == 'exit' and username == self.username:
#                 self.sock.close()
#                 break
#             elif message == 'exit':
#                 print(f'{username} leave chat')
#             else:
#                 print(f'{username} : {message}')


#     # 入力の文字数チェック
#     def is_valid_length(self, input: str, length: int) -> bool:
#         l: int = len(input)
#         return 0 < l and l <= length

#     # ユーザ名入力、エンコード
#     def input_username(self) -> str:
#         while not self.is_valid_length(self.username, 10):
#             self.username = input('user name(Up to 10 characters): ')
        
#         return self.username
    
#     # ポート入力
#     def inputPort(self) -> None:
#         while not self.is_valid_length(str(self.clientPort), 5):
#             port = input('port(Up to 5 digits): ')
#             self.clientPort = int(port)
    
#     # 送信時間経過チェック
#     def check_timeout(self) -> bool:
#         return time.perf_counter() - self.lastSendTime >= 60

#     # 接続
#     def communicate(self) -> None:
#         # ポート入力
#         self.inputPort()

#         # ソケットとの紐づけ
#         self.set_bind()

#         # ユーザ名入力
#         usernameBits = self.input_username().encode('utf-8')

#         self.usernamelen = len(usernameBits)

#         print("\nChat start!\nif you want to leave, enter 'exit'\n")

#         # スレッドの作成、実行
#         sendThread: threading.Thread = threading.Thread(target=self.send)
#         receiveThread: threading.Thread = threading.Thread(target=self.receive)

#         sendThread.start()
#         receiveThread.start()

#         sendThread.join()
#         receiveThread.join()

#         print('close connection')
#         self.sock.close()

def main():
    tcp_client_chat: TcpClient = TcpClient()
    tcp_client_chat.communication()
    
    # udp_client_chat: UdpClient = UdpClient()
    # udp_client_chat.communicate()

main()
