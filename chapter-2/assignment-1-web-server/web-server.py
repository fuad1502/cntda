import socket
import sys

# Setup socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverPort = 1502
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
# Serving loop
while True:
    # Accept connection
    connectionSocket, clientAddress = serverSocket.accept()
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
        # Close connection
        connectionSocket.close()
        print('Served file')
    except IOError:
        # Send HTTP status 404
        httpStatus = 'HTTP/1.1 404 Not Found\r\n'
        connectionSocket.send(httpStatus.encode())
        # Send content-length header line
        httpHeader = 'Content-Length: 0\r\n';
        connectionSocket.send(httpHeader.encode())
        connectionSocket.send('\r\n'.encode())
        # Close connection
        connectionSocket.close()
        break
# Close server
serverSocket.close()
print('Closed server')
sys.exit()
