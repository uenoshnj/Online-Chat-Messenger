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

class Udp_Server:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001

        self.buffer: int = 4096
        self.user_dict: dict[str, list] = {}

    # ソケット紐づけ
    def setBind(self) -> None:
        self.sock.bind((self.serverHost, self.serverPort))
    
    # データ送信
    def send(self, sendData: bytes) -> None:        
        for address in self.user_dict.values() :
            self.sock.sendto(sendData, address)


    # データ受信
    def receive(self) -> bytes:
        recvdata: bytes
        address: tuple[str, int]
        username: str
        msg: str

        recvdata, address = self.sock.recvfrom(4096)
        recvdata_str: str = recvdata.decode('utf-8')
        username, msg = recvdata_str.split(':')
        time_start: float = time.perf_counter()
        self.user_dict[username[1:]] = [address, time_start]
    
        return recvdata
    
    # リレーシステムからユーザを削除
    def deleteTimeOverUser(self, username: str) -> None:
        for user in self.user_dict.keys():
            if time.perf_counter() - self.user_dict[user][1] >= 60:
                del self.user_dict[user]
    



# DPATH = 'temp'
# MESSAGELOG = 'message.log'
# SERVER_ADDRESS = '0.0.0.0'
# SERVER_PORT = 9001

# # メッセージ保存用ディレクトリの作成
# if not os.path.exists(DPATH):
#     os.makedirs(DPATH)

# # 接続中のユーザ
# user_dict = {}

# # UDPソケット作成
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# print(f'starting up on port {SERVER_PORT}')

# # アドレス紐づけ
# sock.bind((SERVER_ADDRESS, SERVER_PORT))

# try:
#     while True:
#         # ヘッダを受信し、ユーザ名の長さとデータの長さを変数に格納
#         header = sock.recv(5)
#         usernamelen = int.from_bytes(header[:1])
#         data_length = int.from_bytes(header[1:])

#         # ユーザ名取得
#         username = sock.recv(usernamelen).decode()

#         # データ(メッセージ)を受信
#         data, address = sock.recvfrom(data_length)
#         message = data.decode()

#         # ユーザ名が既に存在している場合、メッセージを返却。
#         if username in user_dict.keys() and address[1] not in user_dict.values():
#             sock.sendto(b'user is already exist!', address)
#             continue

#         # クライアントからexitを受け取った場合、ユーザ削除
#         if message == 'exit':
#             user_dict.pop(username)
#         # それ以外の場合
#         else:
#             # key：ユーザ名, value：アドレスで辞書に格納
#             if username not in user_dict.keys():
#                 user_dict[username] = address

#             # ユーザ名：メッセージの形式でファイルに保存
#             user_message = f'{username}: {message}'
#             with open(os.path.join(DPATH, MESSAGELOG), 'a') as f:
#                 f.write(user_message + '\n')

#             # 接続中のすべてのクライアントにメッセージを送信
#         for value in user_dict.values():
#             sock.sendto(user_message.encode(), value)


# except OSError as e:
#     print(f'OSerror: {e}')

# except Exception as e:
#     print(f'Exception: {e}')

# finally:
#     sock.close()
