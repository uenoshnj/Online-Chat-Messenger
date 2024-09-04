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

class Tcp_Client:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001
        self.clientHost: str = ''
        self.clientPort: int = 0

        self.roomName: str = ''
        self.userName: str = ''
        self.operation: int = 0
        self.state: int = 0


    # 接続
    def connect(self) -> None:
        try:
            self.sock.connect((self.serverHost, self.serverPort))
        
        except OSError as err:
            print(f'error : {err}')
            sys.exit(1)
    
    # チャットルーム作成
    def createRoom(self) -> None:
        return 0
    
    # チャットルーム参加
    def joinRoom(self) -> None:
        return 0
    
    # ヘッダープロトコル作成
    def createHeaderProtocol(self, roomNameLength: int, operationLength: int, stateLength: int, payloadSize: int) -> bytes:
        return \
            roomNameLength.to_bytes(1, 'big') + \
            operationLength.to_bytes(1, 'big') + \
            stateLength.to_bytes(1, 'big') +\
            payloadSize.to_bytes(29, 'big')
    
    # 長さチェック
    def isValidLength(self, input: str, length: int) -> bool:
        l: int = len(input)
        return 0 < l and l <= length

    # ルーム名の入力
    def inputRoomName(self) -> bytes:
        while not self.isValidLength(self.roomName, 20):
            self.roomName = input('room name(Up to 20 characters) : ')
        
        return self.roomName.encode('utf-8')

    # ユーザ名の入力
    def inputUsername(self) -> bytes:
        while not self.isValidLength(self.userName, 10):
            self.userName = input('user name(Up to 10 characters) : ')
        
        return self.userName.encode('utf-8')
    
    # 操作の入力
    def inputOperation(self) -> bytes:
        while self.operation != 1 or self.operation != 2:
            self.operation = int(input('input operation(1 or 2) : '))
        
        return self.operation.to_bytes(1, 'big')
    

    # サーバ初期化依頼
    def serverInit(self, tcrp: bytes) -> None:
        try:
            self.sock.sendto(tcrp, (self.serverHost, self.serverPort))
        
        except OSError as e:
            print(f'error: {e}')
        
        finally:
            self.sock.close()
            sys.exit(1)
    
    # データ受信
    def receive(self) -> None:
        self.sock.recv()

    #
    def communication(self) -> None:
        # サーバへ接続
        self.connect()

        # ルーム名、ユーザ名、操作の入力
        roomNameBits: bytes = self.inputRoomName()
        roomNameBitsLen: int = len(roomNameBits)

        usernameBits: bytes = self.inputUsername()
        usernameBitsLen: int = len(usernameBits)

        operationBits: bytes = self.inputOperation()
        operationBitsLen: int = len(operationBits)

        if self.operation == 1:
            # パスワードの入力
            passward = input('password : ')


        stateBits: bytes = self.state.to_bytes(1, 'big')
        stateBitsLen: int = len(stateBits)
        
        header: bytes = self.createHeaderProtocol(roomNameBitsLen, operationBitsLen, stateBitsLen, usernameBitsLen)

        body: bytes = roomNameBits + usernameBits

        tcpr: bytes = header + body

        self.serverInit(tcpr)

        # 準拠
        data: bytes = self.sock.recv(4096)

        # 完了
        data: bytes = self.sock.recv(4096)

        return token









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
    tcp_client_chat: Tcp_Client = Tcp_Client()
    
    udp_client_chat: Udp_Client = Udp_Client()
    udp_client_chat.communicate()

main()
