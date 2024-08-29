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

class Udp_Client:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001
        self.clientHost: str = '127.0.0.1'
        self.clientPort: int = 999999

        self.username: str = ''
        self.usernamelen: int = 0
        self.buffer: int = 4096
        self.lastSendTime: float = 0

        self.faultCount: int = 0

    # ソケット紐づけ
    def setBind(self) -> None:
        self.sock.bind((self.clientHost, self.clientPort))
        self.lastSendTime = time.perf_counter()

    # データ送信
    def send(self) -> None:
        while True:    
            message: str = input()
            if self.checkTimeout():
                message = 'exit'
                print('Time out!')
            data: bytes = self.usernamelen.to_bytes(1, 'big') + f'{self.username}{message}'.encode('utf-8')
            self.sock.sendto(data, (self.serverHost, self.serverPort))
            self.lastSendTime = time.perf_counter()

            if message == 'exit':
                self.sock.close()
                break

    
    # データ受信
    def receive(self) -> None:
        while True:
            data: bytes = self.sock.recv(self.buffer)
            usernamelen = int.from_bytes(data[:1], 'big')
            username = data[1:1+usernamelen].decode('utf-8')
            message = data[1+usernamelen:].decode('utf-8')

            if message == 'exit' and username == self.username:
                self.sock.close()
                break
            elif message == 'exit':
                print(f'{username} leave chat')
            else:
                print(f'{username} : {message}')


    # 入力の文字数チェック
    def isValidLength(self, input: str, length: int) -> bool:
        l: int = len(input)
        return 0 < l and l <= length

    # ユーザ名入力、エンコード
    def inputUsername(self) -> str:
        while not self.isValidLength(self.username, 10):
            self.username = input('user name(Up to 10 characters): ')
        
        return self.username
    
    # ポート入力
    def inputPort(self) -> None:
        while not self.isValidLength(str(self.clientPort), 5):
            port = input('port(Up to 5 digits): ')
            self.clientPort = int(port)
    
    # 送信時間経過チェック
    def checkTimeout(self) -> bool:
        return time.perf_counter() - self.lastSendTime >= 60

    # 接続
    def communicate(self) -> None:
        # ポート入力
        self.inputPort()

        # ソケットとの紐づけ
        self.setBind()

        # ユーザ名入力
        usernameBits = self.inputUsername().encode('utf-8')

        self.usernamelen = len(usernameBits)

        print("\nChat start!\nif you want to leave, enter 'exit'\n")

        # スレッドの作成、実行
        sendThread: threading.Thread = threading.Thread(target=self.send)
        receiveThread: threading.Thread = threading.Thread(target=self.receive)

        sendThread.start()
        receiveThread.start()

        sendThread.join()
        receiveThread.join()

        print('close connection')
        self.sock.close()

def main():
    udp_client_chat: Udp_Client = Udp_Client()
    udp_client_chat.communicate()

main()
