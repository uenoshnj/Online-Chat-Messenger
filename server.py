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
import threading
import sys

DPATH = 'temp'
MESSAGELOG = 'message.log'
SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 9001

# メッセージ保存用ディレクトリの作成
if not os.path.exists(DPATH):
    os.makedirs(DPATH)

# 接続中のユーザ辞書
user_dict = {}

# UDPソケット作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f'starting up on port {SERVER_PORT}')

# アドレス紐づけ
sock.bind((SERVER_ADDRESS, SERVER_PORT))

while True:
    # ヘッダを受信し、ユーザ名の長さとデータの長さを変数に格納
    header = sock.recv(5)
    print(header)
    usernamelen = int.from_bytes(header[:1])
    data_length = int.from_bytes(header[1:])

    # ユーザ名取得
    username = sock.recv(usernamelen).decode()
    print(username)

    # データ(メッセージ)を受信
    data, address = sock.recvfrom(data_length)
    print(f'Received {len(data)} bytes from {address}')
    message = data.decode()

    # ユーザとの接続削除
    if message == 'end':
        print(f'{username} logged out')
        user_dict.pop(username)

    # key：ユーザ名, value：アドレスで辞書に格納
    if username not in user_dict.keys():
        user_dict[username] = address

    # ユーザ名：メッセージの形式で標準出力
    user_message = f'{username}: {message}'
    print(user_message)


    # ユーザ名：メッセージの形式でファイルに保存
    with open(os.path.join(DPATH, MESSAGELOG), 'a') as f:
        f.write(user_message + '\n')
        print('logged the message')

    # 接続中のすべてのクライアントにメッセージを送信
    print('now online: ')
    for key in user_dict.keys():
        print(key)

    for value in user_dict.values():
        print(value)
        sock.sendto(user_message.encode(), value)
