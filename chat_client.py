# 客户端
from socket import *
from multiprocessing import Process, Queue
import sys
import re
from time import sleep

ADDR = ('127.0.0.1', 8888)


# 请求进入聊天室
def in_chat(udp_socket):
    while True:
        try:
            name = input('请输入姓名：')
        except:
            sys.exit()
        name = ''.join(name.split(' '))
        w = re.findall(r'\W|_', name)
        if w:
            print('不允许有特殊符号，重新输入姓名')
            continue
        msg = 'L %s' % name
        udp_socket.sendto(msg.encode(), ADDR)
        data, addr = udp_socket.recvfrom(200)
        if data.decode() == 'ok':
            print('进入聊天室')
            return name
        elif data.decode() == 'Xx':
            print('黑名单,禁止进入')
            return 'NO'
        print(data.decode())


# 接收消息
def get_msg(udp_socket, q):
    global BLACK
    while True:
        try:
            data, addr = udp_socket.recvfrom(5000)
        except:
            return
        if data.decode() == 'Xx':
            q.put('Xx')
            return
        print(data.decode(), '\n请输入消息,QUIT退出：', end='')


# 发送消息
def put_msg(udp_socket, name, q):
    while True:
        sleep(0.3)
        if q.qsize():
            print('已被拉入黑名单')
            udp_socket.close()
            q.close()
            return
        try:
            text = input('请输入消息,QUIT退出：')
        except KeyboardInterrupt:
            text = 'QUIT'
        if text == 'QUIT':
            msg = 'Q %s' % name
            udp_socket.sendto(msg.encode(), ADDR)
            sys.exit('退出聊天室')
        msg = 'C %s %s' % (name, text)
        udp_socket.sendto(msg.encode(), ADDR)


# 启动函数
def main():
    q = Queue()
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    name = in_chat(udp_socket)
    if name == 'NO':
        q.close()
        udp_socket.close()
        return
    recv_p = Process(target=get_msg, args=(udp_socket, q))
    recv_p.daemon = True
    recv_p.start()
    put_msg(udp_socket, name, q)


if __name__ == '__main__':
    main()
