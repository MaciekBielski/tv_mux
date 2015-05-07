import socket, pickletools
from muxCommon import *

table = set()
isLogged = False

def helloAck(arg=None):
  """ on HELLO """
  global isLogged
  isLogged = True
  return ('OK',None)

def showAll(data=None):
  """ on RS """
  global table
  out = ''
  if len(table)>0:
    for el in sorted(table,key=lambda e: e.mcId):  
      out += el.__str__()+'\n'
  else:
    out = ' [+] No records found'
  return ('OK',bytes(out,'UTF-8'))

def addRecord(data=None):
  """ on ADD """
  global table
  cnt=0
  dataRows = [ (e+b'.') for e in data.split(b'.')[:-1]]
  for obj in [ pickle.loads(r) for r in dataRows ]:
    if obj not in table:
      cnt +=1
      table.add(obj)
  raport = ' [+] {0:3d} rows has been inserted'.format(cnt)
  return ('OK',bytes(raport,'UTF-8'))

def delRecord(data=None):
  """ on DEL """
  global table
  cnt=0
  dataSet = set(data)
  toDelete = set()
  for el in sorted(table,key=lambda e: e.mcId):
    if el.mcId in sorted(dataSet):
      cnt +=1
      toDelete.add(el)
  table.difference_update(toDelete)
  raport = ' [+] {0:3d} rows has been removed'.format(cnt)
  return ('OK',bytes(raport,'UTF-8'))

def dropTable(data=None):
  """ on DROP """
  global table
  raport = ' [+] {0:3d} rows has been removed'.format(len(table))
  table.clear()
  return ('OK',bytes(raport,'UTF-8'))

def dispatch(cmd,data):
  """ gets the command and calls corresponding function """
  fun = {
      'HELLO': helloAck,
      'RS': showAll,
      'ADD': addRecord,
      'DEL': delRecord,
      'DROP': dropTable
      }.get(cmd,None)
  if fun!=None:
    return fun(data)
  else:
    print('[-] Error! Bad command')

################# EXECUTION ##################
port=9998
serverSock = socket.socket()
serverSock.bind(('',port))
serverSock.listen(2)
print('Server is running...')
connSock=None
while True:
  connSock, address = serverSock.accept() 
  with connSock.makefile('rwb',buffering=0) as fs:
    while True:
      try:
        respMsg, respData = dispatch(*receiveMsg(fs))
        sendMsg(fs,respMsg, respData)
      except:
        isLogged = False;
        break
connSock.close()
