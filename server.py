#! /usr/bin/env python
import socket as socketlib
import time

HOST = '192.168.2.2'  # Standard loopback interface address (localhost)
PORT = 1111        # Port to listen on (non-privileged ports are > 1023)

s = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)

s.bind((HOST, PORT))
s.listen(0)
print 'Listening on {}'.format(PORT)
(conn,addr)= s.accept()
print 'Connected by {}'.format(addr)
while True:
#    (conn, addr) = s.accept()
#    print('Connected by', addr)
    try:
        time.sleep(1)
        data = conn.recv(1)
        if len(data) == 0:
            print 'Connected lost from {}'.format(addr)
            print 'Waiting for new connection {}'.format(addr)
            (conn, addr) = s.accept()
        else:
            print 'Received: {}'.format(data)
    except socket.error:
        break
s.shutdown(socketlib.SHUT_RDWR)
s.close()

