import socket
import sys
import os.path
import json
import multiprocessing
import threading
from thread import *
from collections import deque
 
HOST = '' #For future hosting, aka AWS
PORT = 6960
USERS_FILE = '/Users/ronen/Encrypchat/All-Users.json'

#queue.close()
#queue.join_thread()
#p.join()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'

s.listen(10)
print 'Socket now listening on ' + socket.gethostbyname(socket.gethostname()) + ':' + str(PORT)


users = None


tmpf = open(USERS_FILE, 'r')
if len(tmpf.read()) > 1:
    tmpf.seek(0,0)
    users = json.load(tmpf)
else:
    users = dict()
tmpf.close()

def userExists(user):
    global users
    f = open(USERS_FILE, 'r')
    if len(f.read()) > 1:
        f.seek(0,0)
        users = json.load(f)
        f.seek(0,0)
        f.close()
        if users.get(user, '') == '':
            return False
        else:
            return True
    else:
        return False

def userExistsByDict(user):
    global users
    if users.get(user, '') == '':
        return False
    else:
        return True

def registerUser(num, pk):
    global users
    print 'NUM ' + num
    print 'PK ' + pk
    f = open(USERS_FILE, 'r')
    f.seek(0,0)
    if len(f.read()) > 1:
        f = open(USERS_FILE, 'w')
        print 'opened'
        users[num] = pk
        print 'set user dict'
        f.seek(0,0)
        print 'seeked'
        json.dump(users, f)
        print 'dumped'
        f.close()
        print 'closed'
        print 'Created user ' + num
        return '0\n'
    else:
        f = open(USERS_FILE, 'w+')
        users = dict()
        users[num] = pk
        f.seek(0,2)
        json.dump(users, f)
        print 'Created table + user ' + num
        f.close()
        return '0\n'
    print 'return err'

msgDict = dict()

def clientthread(conn):
    sourceNumber = ''
    while True:
        dataJson = conn.recv(4096)
        if not dataJson:
            print 'Disconnected from ' + sourceNumber
            break
        data = json.loads(dataJson)
        reqtype = data['reqtype']
        sourceNumber = data['from']
        
        if reqtype == 2:
            print 'registering'
            a = registerUser(sourceNumber, data['content'])
            conn.sendall(a)
            print 'result: ' + a
        elif reqtype == 3:
            targetNumber = data['to']
            print 'Requested PK for ' + targetNumber
            conn.sendall(users[targetNumber] + '\n')
        elif reqtype == 1:
            if msgDict.get(sourceNumber, None) == None:
                conn.sendall('0\n')
            elif not msgDict[sourceNumber]:
                conn.sendall('0\n')
            else:
                conn.sendall(msgDict[sourceNumber].pop())
        elif reqtype == 0:
            targetNumber = data['to']
            message = data['content']
            key = targetNumber
            if msgDict.get(key, None) == None:
                msgDict[key] = deque()
            msgDeque = msgDict[key]
            msgDeque.appendleft(dataJson)
            print 'sent a message to ' + targetNumber + ' from ' +sourceNumber
            conn.sendall('0\n')
    conn.close()
while 1:
    conn, addr = s.accept()
    print 'Connected to ' + addr[0] + ':' + str(addr[1])
    start_new_thread(clientthread ,(conn,))
 
s.close()
