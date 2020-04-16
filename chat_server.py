# 服务端
from socket import *
from multiprocessing import Process
import re

ADDR = ('127.0.0.1', 8888)
USER = {}  # {'name','address'}
BLACK = {}  # {'address',count}


# 处理进入聊天室请求
def in_chat(udp_socket, name, address):
    # 查看用户是否在黑名单
    if address[0] in BLACK and BLACK[address[0]] == 3:
        udp_socket.sendto(b'Xx', address)
        return
    # 查看用户是否重名
    elif name in USER or '管理' in name:
        udp_socket.sendto('用户已经存在'.encode(), address)
        return
    # 用户可以进入聊天室
    udp_socket.sendto(b'ok', address)
    msg = '\n欢迎 %s 进入聊天室' % name
    for addr in USER.values():
        udp_socket.sendto(msg.encode(), addr)
    USER[name] = address
    BLACK[address[0]] = 0


# 给其他用户发送消息
def put_msg(udp_socket, name, text, addr):
    black_msg = 'aa|bb|oo'  # 设置敏感词汇
    data = re.findall(black_msg, text)
    # 判断是否有敏感词汇
    if data:
        BLACK[addr[0]] += 1
        msg = '管理员:警告%s有敏感词汇,警告%d次' % (name, BLACK[addr[0]])
        if BLACK[addr[0]] == 3:
            data = b'Xx'
            udp_socket.sendto(data, addr)
            msg = '管理员:%s被踢出该群' % name
            del USER[name]
        for i in USER:
            udp_socket.sendto(msg.encode(), USER[i])
        return
    msg = '\n%s : %s' % (name, text)
    # 为其他成员发送消息
    for i in USER:
        if i != name:
            udp_socket.sendto(msg.encode(), USER[i])


# 处理用户退出
def user_out(udp_socket, name):
    try:
        del USER[name]
    except:
        return
    msg = '\n%s 退出聊天室' % (name)
    for i in USER:
        udp_socket.sendto(msg.encode(), USER[i])


# 处理客户端请求
def get_request(udp_socket):
    while True:
        try:
            data, addr = udp_socket.recvfrom(5000)
        except:
            return
        if not data:
            continue
        msg = data.decode().split(' ', 2)
        if msg[0] == 'L':
            in_chat(udp_socket, msg[1], addr)
        elif msg[0] == 'C':
            put_msg(udp_socket, msg[1], msg[2], addr)
        elif msg[0] == 'Q':
            user_out(udp_socket, msg[1])


# 发送管理员消息
def sudo_put(udp_socket):
    while True:
        try:
            text = input('管理员：')
        except:
            return
        msg = 'C 管理员 %s' % text
        udp_socket.sendto(msg.encode(), ADDR)


# 启动函数
def main():
    udp_socket = socket(AF_INET, SOCK_DGRAM)
    udp_socket.bind(ADDR)
    p = Process(target=get_request, args=(udp_socket,))
    p.start()
    sudo_put(udp_socket)
    p.join()


if __name__ == '__main__':
    main()
