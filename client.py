'''
# オンラインチャットプログラム（クライアント）
    ・概要
    サーバへ接続し、メッセージを送信する。

    ・プロトコル
    ヘッダー : ユーザ名の長さ（1バイト）+ メッセージの長さ（4バイト）
    データ : メッセージ本文
'''

import socket
import sys
import os


# サーバのアドレス、ポート
SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 9001

# クライアントのアドレス
ADDRESS = ''

# チャットのタイムアウト時間(秒)
TIMEOUT = 30

# メッセージ送信失敗最大回数
MAXSENDCOUNT = 3

# 接続削除用
CLOSECONNECTION = 'exit'

class Udp_Client:
    def __init__(self):
        self.username = self.readInput(255, 'name')
        self.port = int(self.readInput(5, 'port'))

    # ユーザの入力を読み込み
    def readInput(self, length, question):
        maxLength = length + 1
        while maxLength > length:
            userInput = input(f'{question}: ')
            maxLength = len(userInput)
            if maxLength > length - 1:
                print(f'{question} up to {length}')
        return userInput
    
    def getUserName(self):
        return self.username
    
    def getPort(self):
        return self.port


# ヘッダー情報のフォーマット
def protocolHeader(usernameLen, dataLen):
    return usernameLen.to_bytes(1) + dataLen.to_bytes(4)

# UDPソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f'Connected {SERVER_ADDRESS}:{SERVER_PORT}')

# ユーザ情報作成
client = Udp_Client()

userNameBits = client.getUserName().encode()

# 接続の紐づけ
sock.bind((ADDRESS, client.getPort()))

print('\nChat start!\n'\
    "if you want to leave, Enter 'exit'\n")

# タイムアウトの設定
sock.settimeout(30)

# 子プロセスの作成
pid = os.fork()

# 子プロセスの場合、メッセージ送信
if pid == 0:
    try:
        while True:
            # メッセージの入力
            userMessage = input()
            userMessageBits = userMessage.encode()

            # ヘッダの作成
            header = protocolHeader(len(userNameBits), len(userMessageBits))

            # ヘッダの送信
            sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

            # ユーザ名の送信
            sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))

            if userMessage == CLOSECONNECTION:
                sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
                break
            # メッセージの送信
            else:
                sock.sendto(userMessageBits, (SERVER_ADDRESS, SERVER_PORT))
            

    except TimeoutError as e:
        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(userMessageBits))

        # ヘッダの送信
        sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

        # ユーザ名の送信
        sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
        print(f'error: {e}')

    except OSError as e:
        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(userMessageBits))

        # ヘッダの送信
        sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

        # ユーザ名の送信
        sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))

        sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
        print(f'error: {e}')
    
    except Exception as e:
        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(userMessageBits))

        # ヘッダの送信
        sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

        # ユーザ名の送信
        sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
        sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
        print(f'error: {e}')

    finally:
        print('Disconnect')
        sock.close()
        sys.exit(1)

# 親プロセスの場合、メッセージ受信
else:
    try:
        while True:
            # メッセージの受信
            data, server = sock.recvfrom(4096)
            print(data.decode())

    except OSError as e:
        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(CLOSECONNECTION))

        # ヘッダの送信
        sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

        # ユーザ名の送信
        sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
        sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
        print(f'error: {e}')
    
    except Exception as e:
        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(CLOSECONNECTION))

        # ヘッダの送信
        sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT))

        # ユーザ名の送信
        sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT))
        
        sock.sendto(CLOSECONNECTION.encode(), (SERVER_ADDRESS, SERVER_PORT))
        print(f'error: {e}')
    
    finally:
        print('Disconnect')
        sock.close()
        sys.exit(1)
