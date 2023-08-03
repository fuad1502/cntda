import socket
import sys
import threading

# Setup socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverPort = 1502
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

# Serving thread
def serveConnection(connectionSocket):
    # Receive message
    message = connectionSocket.recv(1024)
    # Extract file name
    fileName = message.split()[1]
    print('Requested file: ', fileName)
    try:
        # Open file
        f = open(fileName[1:])
        # Read file
        outputData = f.read()
        # Send HTTP status 200
        httpStatus = 'HTTP/1.1 200 OK\r\n'
        connectionSocket.send(httpStatus.encode())
        # Send content-length header line
        httpHeader = 'Content-Length: ' + str(len(outputData)) + '\r\n';
        connectionSocket.send(httpHeader.encode())
        connectionSocket.send('\r\n'.encode())
        # Send requested file
        for i in range(0, len(outputData)):
            connectionSocket.send(outputData[i].encode())
        connectionSocket.send('\r\n'.encode())
        print('Served file')
    except IOError:
        # Send HTTP status 404
        httpStatus = 'HTTP/1.1 404 Not Found\r\n'
        connectionSocket.send(httpStatus.encode())
        # Send content-length header line
        httpHeader = 'Content-Length: 0\r\n';
        connectionSocket.send(httpHeader.encode())
        connectionSocket.send('\r\n'.encode())
        print('Requested file not found')
    # Close connection
    connectionSocket.close()

# Serving loop
try:
    while True:
        # Accept new connection
        connectionSocket, clientAddress = serverSocket.accept()
        # Create new thread
        thread = threading.Thread(target=serveConnection, args=(connectionSocket,))
        thread.start()
except KeyboardInterrupt:
    serverSocket.close()
    print('Closed server')
    sys.exit()
