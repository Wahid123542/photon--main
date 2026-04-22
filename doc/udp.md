# About UDP

## General system overview

In communications using UDP, a client program sends a message packet to a destination server wherein the destination server also runs on UDP.

## Function flow

The information flow starts from the client making a request to the server.

### UDP server
1. create socket: socket()
2. bind to port: bind()
3. receive data: recvfrom()
4. send reply: sendto()
5. server exit: close()


### UDP client
1. create socket: socket()
2. bind to port: bind()
3. send data: sendto()
4. receive reply: recvfrom()
5. client exit: close()

## Data scheme
(TODO)

## Function design
(TODO)
