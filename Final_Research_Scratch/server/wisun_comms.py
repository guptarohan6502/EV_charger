import socket


def send_toserver(msg, sock_send, UDP_IP, UDP_PORT):
    MESSAGE = msg

    message_bytes = str.encode(MESSAGE)

    sock_send.sendto(message_bytes, (UDP_IP, UDP_PORT))


def recv_fromserver(sock_recv):
    data, addr = sock_recv.recvfrom(1024)  # buffer size is 1024 bytes
    # convert from binart to string
    data = data.decode('utf-8')
    print(data, type(data))
    return data


def send_rec_server(msg, sock_send, sock_recv, UDP_IP, UDP_PORT):
    send_toserver(msg, sock_send, UDP_IP, UDP_PORT)
    return recv_fromserver(sock_recv)
