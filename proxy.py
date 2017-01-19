#!/usr/bin/env python

import socket, os, sys, errno, select

#AF_INET means we want an IPv4 socket
#SOCK_STREAM means we want a TCP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind a port to listen to
#0.0.0.0 <- listen on all addresses on the network
serverSocket.bind(("0.0.0.0", 8000))

#the 5 indicates how many clients it will allow before it sends clients away
serverSocket.listen(5)

while True:
    #creates a socket for the client connecting and the address of who connected
    (incomingSocket, address) = serverSocket.accept()
    print("Got a connection from: %s" % (repr(address)))

    try:
     reaped = os.waitpid(0, os.WNOHANG)
    except OSError, e:
                if e.errno == errno.ECHILD:
                    pass
                else:
                    raise
    else:
        print("Reaped %s" % (repr(reaped)))

    if (os.fork() !=0):
        continue

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect(("www.google.com", 80))

    incomingSocket.setblocking(0)
    clientSocket.setblocking(0)

    while True:
        request = bytearray()
        while True:
            try:
                part = incomingSocket.recv(1024)
            except IOError, e:
                if e.errno == socket.errno.EAGAIN:
                    break
                else:
                    raise

            if(part):
                request.extend(part)
                clientSocket.sendall(part)
            else:
                sys.exit(0) #quit the program

        if len(request) > 0:
            print(request)

        response = bytearray()
        while True:
            try:
                part = clientSocket.recv(1024)
            except IOError, e:
                if e.errno == socket.errno.EAGAIN:
                    break
                else:
                    raise

            if(part):
                response.extend(part)
                incomingSocket.sendall(part)
            else:
                sys.exit(0) #quit the program

        if len(response) > 0:        
            print(response)

        #Prevents using 100% of CPU
        select.select(
            [incomingSocket, clientSocket], #read
            [],                             #write
            [incomingSocket, clientSocket], #exceptions
            1.0                             #timeout
        )