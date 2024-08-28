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

class Udp_Client:
    def __init__(self) -> None:
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverHost: str = '0.0.0.0'
        self.serverPort: int = 9001
        self.clientHost: str = '127.0.0.1'
        self.clientPort: int = 9050

        self.username: str = ''
        self.usernamelen: int = 0
        self.buffer: int = 4096

        self.faultCount: int = 0

    # ソケット紐づけ
    def setBind(self) -> None:
        self.sock.bind((self.clientHost, self.clientPort))

    # データ送信
    def send(self) -> None:
        while True:
            message: str = input()
            data: bytes = self.usernamelen.to_bytes(1, 'big') + f'{self.username}{message}'.encode('utf-8')
            self.sock.sendto(data, (self.serverHost, self.serverPort))

            if message == 'exit':
                self.sock.close()
                break

    
    # データ受信
    def receive(self) -> None:
        while True:
            data: bytes = self.sock.recv(self.buffer)
            message = data.decode('utf-8')

            if message[message.find(':') + 1:] == 'exit':
                self.sock.close()
                break

            print(message)


    # 入力の文字数チェック
    def isValidLength(self, input: str, len: int) -> bool:
        l: int = len(input)
        return 0 < l and l <= len

    # ユーザ名入力、エンコード
    def inputUsername(self) -> None:
        while not self.isValidLength(self.username, 10):
            self.username = input('User name(Up to 10 characters): ')
        
        return self.username.encode('utf-8')

    # 接続
    def communicate(self) -> None:
        print(f'Connected {self.serverAddress}')

        # ソケットとの紐づけ
        self.setBind()

        # ユーザ名入力の呼び出し、エンコード
        usernameBits = self.inputUsername()

        self.usernamelen = len(usernameBits)

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
    udp_client_chat.setBind()
    udp_client_chat.communicate()


# # サーバのアドレス、ポート
# SERVER_ADDRESS = '0.0.0.0'
# SERVER_PORT = 9001

# # クライアントのアドレス
# ADDRESS = ''

# # チャットのタイムアウト時間(秒)
# TIMEOUT = 30

# # メッセージ送信失敗最大回数
# MAXSENDCOUNT = 3

# # 接続削除用
# CLOSECONNECTION = 'exit'

# # ヘッダー情報のフォーマット
# def protocolHeader(usernameLen, dataLen):
#     return usernameLen.to_bytes(1) + dataLen.to_bytes(4)

# # UDPソケットの作成
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# print(f'Connected {SERVER_ADDRESS}:{SERVER_PORT}')

# # ユーザ情報作成
# client = Udp_Client()

# userNameBits = client.getUserName().encode()

# # 接続の紐づけ
# sock.bind((ADDRESS, client.getPort()))

# print('\nChat start!\n'\
#     "if you want to leave, Enter 'exit'\n")

# # タイムアウトの設定
# sock.settimeout(30)

# # 子プロセスの作成
# pid = os.fork()

# # 子プロセスの場合、メッセージ送信
# if pid == 0:
#     try:
#         while True:
#             # メッセージの入力
#             userMessage = input()
#             userMessageBits = userMessage.encode()

#             # ヘッダの作成
#             header = protocolHeader(len(userNameBits), len(userMessageBits))

#             # ヘッダの送信
#             sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#             # ユーザ名の送信
#             sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))

#             if userMessage == CLOSECONNECTION:
#                 sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#                 break
#             # メッセージの送信
#             else:
#                 sock.sendto(userMessageBits, (SERVER_ADDRESS, SERVER_PORT))
            

#     except TimeoutError as e:
#         # ヘッダの作成
#         header = protocolHeader(len(userNameBits), len(userMessageBits))

#         # ヘッダの送信
#         sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#         # ユーザ名の送信
#         sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
#         sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#         print(f'error: {e}')

#     except OSError as e:
#         # ヘッダの作成
#         header = protocolHeader(len(userNameBits), len(userMessageBits))

#         # ヘッダの送信
#         sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#         # ユーザ名の送信
#         sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))

#         sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#         print(f'error: {e}')
    
#     except Exception as e:
#         # ヘッダの作成
#         header = protocolHeader(len(userNameBits), len(userMessageBits))

#         # ヘッダの送信
#         sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#         # ユーザ名の送信
#         sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
#         sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#         print(f'error: {e}')

#     finally:
#         print('Disconnect')
#         sock.close()
#         sys.exit(1)

# # 親プロセスの場合、メッセージ受信
# else:
#     try:
#         while True:
#             # メッセージの受信
#             data, server = sock.recvfrom(4096)
#             print(data.decode())

#     except OSError as e:
#         # ヘッダの作成
#         header = protocolHeader(len(userNameBits), len(CLOSECONNECTION))

#         # ヘッダの送信
#         sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#         # ユーザ名の送信
#         sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
#         sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#         print(f'error: {e}')
    
#     except Exception as e:
#         # ヘッダの作成
#         header = protocolHeader(len(userNameBits), len(CLOSECONNECTION))

#         # ヘッダの送信
#         sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

#         # ユーザ名の送信
#         sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
#         sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
#         print(f'error: {e}')
    
#     finally:
#         print('Disconnect')
#         sock.close()
#         sys.exit(1)