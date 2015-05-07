import socket
import struct
from muxCommon import *
from html.parser import HTMLParser

# global table of rows parsed from Wikipedia
muxes = []

class MuxParser(HTMLParser):
  """parser class"""
  tableCnt = 0
  muxCnt = 0
  goParsing = False
  insideRow = False
  insideCell = False
  fillMuxNb = False
  muxNb ='' 
  tmpRow = None
  currCell = 0 

  def handle_starttag(self, tag, attrs):
    # we are parsing only 4 consequtive tables
    if self.tableCnt<4:
      if tag=='table':
        for key, value in attrs:
          if key=='class' and value=='wikitable':
            self.goParsing = True
      elif self.goParsing: 
        if tag=='tr':
          self.tmpRow = dict(muxId='', mux='', channel='', muxOwner='', muxType='')
          self.insideRow = True
        elif tag=='th':
          if self.muxNb == '':
            self.fillMuxNb = True
        elif self.insideRow and tag =='td':
          self.currCell +=1
          self.insideCell = True
    else:
      return


  def handle_endtag(self,tag):
    global muxes
    if tag=='table' and self.goParsing:
      self.goParsing = False
      self.muxNb = ''
      self.tableCnt += 1
    elif self.goParsing:
      if tag=='tr' and self.insideRow:
        # do not add header rows
        if self.tmpRow['channel'] != '':
          self.muxCnt += 1
          self.tmpRow['muxId'] = self.muxCnt
          self.tmpRow['mux'] = self.muxNb
          # parsed data are used to build and object
          muxes.append(MuxChannel(**self.tmpRow))
        self.tmpRow = None
        self.insideRow = False
        self.currCell = 0
      elif tag=='th' and self.fillMuxNb:
        self.fillMuxNb = False
      elif self.insideRow and tag=='td':
        self.insideCell = False

  def handle_data(self, data):
    if self.goParsing:
      if self.fillMuxNb:
        self.muxNb += data
      elif self.insideRow and self.insideCell:
        if self.currCell==1:
          self.tmpRow['channel']+=data
        elif self.currCell==2:
          self.tmpRow['muxOwner']+=data
        elif self.currCell==3:
          self.tmpRow['muxType']+=data

def downloadPage():
  """ Connects with the web and get the body of a page to be parsed """
  data=''
  port=80
  host='en.wikipedia.org'
  sock = socket.socket()
  out = sock.connect((host,port))
  cllf = '\r\n'
  req ='GET http://en.wikipedia.org/wiki/Television_in_Poland HTTP/1.1'+cllf
  req += 'Host: en.wikipedia.org'+cllf
  req += 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0'+cllf
  req += 'Connection: close'+cllf
  req += cllf
  out=sock.sendall(bytes(str(req),'UTF-8'))
  if out!=None:
    print('Sending error')
  with sock.makefile('r',1024,encoding='UTF-8') as fs:
    for line in fs:
      data += line
  sock.close()
  data = data[data.index('<body'):data.index('</body>')+1]
  data = ''.join(data.split('\n'))
  return data

def printResp(byteArg):
  """ Callback that prints the response from a server """
  print(str(byteArg,'UTF-8'))

def showAllLocal(arg=None):
  """ Called on LS """
  if arg!=None:
    print(' [!] Arguments has been ignored')
  global muxes
  print('{0:s} | {1:s} | {2:s} | {3:s} | {4:s}'.format('Id','Name','Channel','Owner','Type'))
  [ print(m) for m in muxes]
  return ('',None,None)

def remoteShow(arg=None):
  """ Called on RS """
  if arg!=None:
    print(' [!] Arguments has been ignored')
  return ('RS',None, printResp)

def remoteAdd(arg=None):
  """ Called on ADD """
  if arg==None:
    print(' [-] I need some arguments!')
  else:
    tmp = [ a.split('-') for a in arg.split(',') ]
    out = []
    # interpretation of elements range or just enumerated elements: 4-6,9,11
    [ (out.extend(list(range(int(t[0])-1,int(t[1])))) if len(t)==2 else out.append(int(t[0])-1)) for t in tmp ]
    # removing duplicated elements
    out = set(out)
    outBytes = bytearray()
    for i in out:    
      outBytes += muxes[i].toBin()
    return ('ADD',outBytes, printResp)

def remoteDel(arg=None):
  """ Called on DEL """
  if arg==None:
    print(' [-] I need some arguments!')
  else:
    tmp = [ a.split('-') for a in arg.split(',') ]
    out = []
    # interpretation of elements range or just enumerated elements: 4-6,9,11
    [ (out.extend(list(range(int(t[0]),int(t[1])+1))) if len(t)==2 else out.append(int(t[0]))) for t in tmp ]
    # removing duplicated elements
    out = set(out)
    return ('DEL',bytes(out),printResp)

def remoteDrop(arg=None):
  """ Called on DROP """
  if arg!=None:
    print(' [!] Arguments has been ignored')
  return ('DROP',None, printResp)

def exeCmd(cmdStr):
  """ Processes user's command and calls corresponding function """
  tmp = cmdStr.strip().split(maxsplit=1)
  cmd = tmp[0]
  args = tmp[1] if len(tmp)==2 else None
  # args
  if cmd=='Q':
    return (cmd,None,None)
  else:
    fun ={
        'LS': showAllLocal,
        'RS': remoteShow,
        'ADD' : remoteAdd,
        'DEL' : remoteDel,
        'DROP' : remoteDrop
        }.get(cmd,None)
    if fun != None:
      return fun(args)  
    else:
      print(' [-] Syntax Error! No such command.')
      return ''

def connectToServer():
  """ Connects to the server and return connected socket """
  serverPort=9998
  serverHost=socket.gethostname()
  s = socket.socket()
  s.connect((serverHost, serverPort))
  return s

def userDialog():
  """ Interaction with a user """
  clientSock = connectToServer()
  with clientSock.makefile('rwb', buffering=0) as fs:
    # pretending loging, not checked in fact
    sendMsg(fs,'HELLO',bytes('qwerty','UTF-8'))
    respMsg,respData=receiveMsg(fs)
    if respMsg=='OK':
      print('logged in')
      while True:
        reqStr, reqData, callbackFun = exeCmd(input('><> '))
        if reqStr=='Q':
          break
        elif reqStr=='':
          continue
        else:
          sendMsg(fs,reqStr,reqData)
          respMsg,respData=receiveMsg(fs)
          if respMsg =='OK':
            if callbackFun != None:
              callbackFun(respData)
      print('Bye')

############## EXECUTION ##########################
mp = MuxParser()
mp.feed(downloadPage())
userDialog()
