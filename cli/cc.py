import socket
import select
import errno
import sys
from threading import Timer, Lock

HEADER_LENGTH = 10

IP = '127.0.0.1'
PORT = 65432

my_username = input('UserName: ')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


username = my_username.encode('utf-8')
username_header = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')
client_socket.send(username_header+username)

mutex = Lock()
message = ''
while True:
    mutex.acquire()

    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header+message)

    try:
        # while True:
        def reciver_refresh():
            # recive things
            try:
                username_header = client_socket.recv(HEADER_LENGTH)

                if not len(username_header):
                    print('[! 1] Connection closed by Server')
                    sys.exit()

                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print("{} > {}\r".format(username, message))
            except:
                pass

            T = Timer(1, reciver_refresh)
            T.start()
        reciver_refresh()
        #message = input('{} > '.format(my_username))
        message = input('')
        mutex.release()

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('[! 2] Reading Trouble:', e)
        continue

    except Exception as e:
        print('[! 3]', e)
