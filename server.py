import socket
import threading
import sys

if len(sys.argv) != 3 :
    print("Correct Usage :server.py <IP address> <port>")
    exit()

IP = str(sys.argv[1])
port = int(sys.argv[2])

server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
#server.bind(("localhost",50001))
server.bind((IP,port))
server.listen(5)

client_list = list()
player_dict = dict()


############# GAME ##############################
board = [" " for i in range(9)]
STATE = "START"
global_sign = ["X" , "O"]
TURN = ""
game_state = ["START" , "PLAYING" , "END" ]

def TicTacToe(board , sign , pos) :
    global STATE
    global player_dict
    global global_sign
    gamescript = ""
    if STATE == "START" :
        gamescript = "Welcome to tic-tac-toe!\n This game our guy should deal who gonna 'X' or 'O' \n \
            then Enter '<X or O> <position>' \n position will show below.\n1|2|3" + "\n" + "4|5|6\n" + "7|8|9\n2 Players need to Enter 'me <O or X>' to choose the sign"
        STATE = "PLAYING"
    elif STATE == "PLAYING" :
        board[pos] = sign
        print(board)
        x = check_board(board)
        print(x)
        if x[0] == "PLAYING" :
            gamescript = show_board(board)
        elif x[0] == "END" :
            gamescript = show_board(board) + \
                "THE WINNER IS " + sign + "! \n Someone Enter 'tic-tac-toe' to play again"
            for i in range(9):
                board[i] = " "
            player_dict.clear()
            TURN = ""
            global_sign.append("X")
            global_sign.append("O")
            STATE = "START"
        else :
            gamescript = show_board(board) + \
                "TIE ! better luck next time \nSomeone Enter 'tic-tac-toe' to play again"
            for i in range(9):
                board[i] = " "
            player_dict.clear()
            TURN = ""
            global_sign.append("X")
            global_sign.append("O")
            STATE = "START"
    return gamescript

def show_board(board):
    s = board[0] + "|" +  board[1] +  "|" + board[2] + "\n" \
       + board[3] + "|" +  board[4] +  "|" + board[5] + "\n" \
       + board[6] + "|" +  board[7] +  "|" + board[8] + "\n"
    return s

def check_board(board):

    x = []
    if board[0] != " " and ( board[0] == board[4] == board[8] ) :
        x = ["END" , board[0]]
    elif board[2] != " " and ( board[2] == board[4] == board[6] ) :
        x = ["END" , board[2]]
    elif board[0] != " " and board[0] == board[1] == board[2] :
        x = ["END" , board[0]]
    elif board[3] != " " and board[3] == board[4] == board[5] :
        x = ["END" , board[3]]
    elif board[6] != " " and board[6] == board[7] == board[8] :
        x = ["END" , board[6]]
    elif board[0] != " " and board[0] == board[3] == board[6] :
        x = ["END" , board[0]]
    elif board[1] != " " and board[1] == board[4] == board[7] :
        x = ["END" , board[1]]
    elif board[2] != " " and board[2] == board[5] == board[8] :
        x = ["END" , board[2]]
    elif " " not in board :
        x = ["DRAW" , " "]
    else :
        x = ["PLAYING" , " "]
    return x

def game_broadcast(gamescript):
    for client in client_list :
        try :
            client.send(bytes(gamescript,"utf-8"))
        except :
            client.close()
            remove(client)

###############################################


def client_thread(conn , addr):
    global client_list
    global player_dict
    global TURN
    global global_sign
    global board
    conn.send(b"Welcome to the server ! , Let's talk each other. ,\n somebody Enter tic-tac-toe to start the game. \n Enter 'rename <new name>' to change your name.")
    name = str(addr[0]) + " : " + str(addr[1])
    while 1 :
        try :
            massage = conn.recv(4096)
            if massage :
                massage_parsing = [e for e in massage.decode("utf-8").split()]
                if len(massage_parsing) >= 2 and massage_parsing[0] == "rename" :
                    name = massage_parsing[1]
                    for i in range(len(client_list)):
                        if client_list[i][0] == conn :
                            client_list[i][1] = name
                print("<" + name + "> : " + str(massage.decode("utf-8")))
                massage_to_send = "<" + name +  "> : " + str(massage.decode("utf-8"))
                broadcast(massage_to_send,conn)
                s = massage.decode("utf-8").strip()
                if s == "tic-tac-toe" and STATE == "START":
                    gamescript = TicTacToe(board," ",-1)
                    game_broadcast(gamescript)
                if STATE == "PLAYING" :
                    board_fill = [e for e in s.split()]
                    gamescript = ""
                    if len(player_dict) < 2 :
                        if len(board_fill) >= 2 and board_fill[0] == "me" and board_fill[1] in global_sign:
                            player_dict[conn] = board_fill[1]
                            global_sign.remove(board_fill[1])
                            if len(player_dict) == 2 :
                                gamescript = "OK! 2 Players can fill now ' " + player_dict[conn] + " ' go first"
                                TURN = conn
                    if conn in player_dict and TURN == conn  and len(board_fill) > 0 and  board_fill[0] in ["X","O"] and board_fill[0] == player_dict[conn]:
                        if len(board_fill) >= 2 and ( board_fill[1] in ["1" , "2", "3" , "4" , "5" , "6" , "7" ,  "8" , "9" ] ) and  board[int(board_fill[1]) - 1] == " " :
                            for e in player_dict :
                                if e != conn :
                                    TURN = e
                            gamescript = TicTacToe(board,player_dict[conn],int(board_fill[1])-1)
                        else :
                            gamescript = "Invalid Position"
                    if gamescript != "" :
                        game_broadcast(gamescript)
            else :
                remove(conn)
        except :
            continue

def broadcast(massage , conn) :
    for client in client_list :
        if client != conn :
            try :
                client.send(bytes(massage,"utf-8"))
            except :
                client.close()
                remove(client)


def remove(conn) :
    if conn in client_list :
        client_list.remove(conn)


while 1 :
    conn , addr = server.accept()
    alias = ""
    client_list.append(conn)
    print(str(addr[0]) + " : " + str(addr[1]) + " connected" )

    t = threading.Thread(target=client_thread , args=(conn , addr))
    t.start()
    #Thread.start_new

conn.close()
server.close()