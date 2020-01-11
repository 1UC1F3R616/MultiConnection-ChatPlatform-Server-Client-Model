import socket
import select

HEADER_LENGTH = 10
IP = ''
PORT = 65432

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}


def recive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except Exception as e:
        print('[!]', e)
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = recive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            # userMessage, expecting tobe username
            clients[client_socket] = user

            print('Accepted New connection from {}:{}, username is {}'.format(
                client_address[0], client_address[1], user['data'].decode('utf-8')))

            for client_socket in clients:
                if client_socket != notified_socket:  # God knows why :/
                    info = 'Welcome {} from {}:{}'.format(
                        user['data'].decode('utf-8'), client_address[0], client_address[1])
                    welcome_ = f"{'1':<{HEADER_LENGTH}}".encode('utf-8')
                    welcome = welcome_ + '>'.encode('utf-8')
                    welcome_ = f"{len(info):<{HEADER_LENGTH}}".encode('utf-8')
                    welcome += welcome_+info.encode('utf-8')
                    client_socket.send(welcome)

        else:
            message = recive_message(notified_socket)

            if message is False:
                print('Closing connection from user {}'.format(
                    clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print('Recived message from {}'.format(
                user['data'].decode('utf-8')))

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(
                        user['header']+user['data']+message['header']+message['data'])

            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
