import socket
import select
import sys
import threading

if len(sys.argv) != 3 :
    print("Correct Usage :clientOnWindow.py <server's IP address> <port>")
    exit()
IP = str(sys.argv[1])
port = int(sys.argv[2])


server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
#server.connect(("localhost" , 50001))
server.connect((IP,port))

def console_write():
    while 1 :
        massage = sys.stdin.readline()
        massage_to_send = bytes(massage,"utf-8")
        try : 
            server.send(massage_to_send)
            sys.stdout.write( "<You> : " )
            sys.stdout.write(massage)
            sys.stdout.flush()
        except :
            print("server is closed")
            server.close()
            break


def sender(socks) :
    while 1 :
        massage = socks.recv(4096)
        print(massage.decode("utf-8"))

t1 = threading.Thread(target=console_write ,args=() )
t2 = threading.Thread(target=sender , args=(server , ))

t1.start()
t2.start()


