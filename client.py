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
import threading

# サーバのアドレス、ポート
SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 9001

# クライアントのアドレス
ADDRESS = ''

# チャットのタイムアウト時間(秒)
TIMEOUT = 30

# メッセージ送信失敗最大回数
MAXSENDCOUNT = 3

# ヘッダー情報のフォーマット
def protocolHeader(usernameLen, dataLen):
    return usernameLen.to_bytes(1) + dataLen.to_bytes(4)

# ユーザの入力を読み込み
def readInput(length, question):
    maxLength = length + 1
    while maxLength > length:
        userInput = input(f'Enter the {question}: ')
        maxLength = len(userInput)
        if maxLength > length - 1:
            print(f'{question} must be {length} characters or less')
    return userInput


# UDPソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f'Connected {SERVER_ADDRESS}:{SERVER_PORT}')

# データ受信
def receiveMsg(sock):
    try:
        while True:
            data, server = sock.recvfrom(4096)
            print(data.decode())
    except:
        pass



try:
    # ユーザ名の入力
    userName = readInput(255, 'name')
    userNameBits = userName.encode()

    # クライアントポートの入力
    port = int(readInput(5, 'port'))

    # 接続の紐づけ
    sock.bind((ADDRESS, port))

    # データ受信開始
    recvThread = receiveMsg(sock)

    recvThread.start()



    while True:
        # メッセージの入力
        userMessage = readInput(4096, 'message')
        userMessageBits = userMessage.encode()

        # ヘッダの作成
        header = protocolHeader(len(userNameBits), len(userMessageBits))

        # ヘッダの送信
        if sock.sendto(header, (SERVER_ADDRESS, SERVER_PORT)):
            sendflg = True

        # ユーザ名の送信
        if sock.sendto(userNameBits, (SERVER_ADDRESS, SERVER_PORT)):
            sendflg = True

        # メッセージの送信
        if sock.sendto(userMessageBits, (SERVER_ADDRESS, SERVER_PORT)):
            sendflg = True

        # メッセージの受信
        data, server = sock.recvfrom(4096)
        print(data.decode())
        
        if userMessage == 'end':
            break

finally:
    print('Closing connection')
    sock.close()