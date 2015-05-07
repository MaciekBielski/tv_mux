import pickle

class MuxChannel():
  """ Class that represent a data record """
  mcId=-1
  mcName=''
  mcChannel=''
  mcOwner=''
  mcType=''

  def __init__(self,**kwargs):
    self.mcId = kwargs['muxId']
    self.mcName = kwargs['mux']
    self.mcChannel = kwargs['channel']
    self.mcOwner = kwargs['muxOwner']
    self.mcType = kwargs['muxType']

  def __str__(self):
    return '{0:d} | {1:s} | {2:s} | {3:s} | {4:s}'.format(self.mcId, self.mcName, self.mcChannel, self.mcOwner, self.mcType)

  def __hash__(self):
    return hash(self.mcId)^hash(self.mcName)^hash(self.mcChannel)^hash(self.mcOwner)^hash(self.mcType)

  def __eq__(self,other):
    return isinstance(other, self.__class__) and self.__hash__()==other.__hash__()
    
  def toBin(self):
    return pickle.dumps(self)

def sendMsg(fs,cmd,data):
  """ Sends a message through the socket.
    fs - handler to the open file-like socket
    cmd - command (as a string)
    data - data of a command (binary)
  """
  dataLen = str(len(data)) if data!=None else '0'
  out = bytes(cmd+'\n'+dataLen+'\n','UTF-8')
  fs.write(out)
  if data!=None:
    fs.write(data)
  fs.flush()

def receiveMsg(fs):
  """
    Receives a message from the socket,
    First line is a command, the second line is the length, the rest is data.    
    The exact amount of data has to be read for correct working.
  """
  cmd = str(fs.readline().strip(),'UTF-8')
  dataSz = int(fs.readline())
  data = fs.read(dataSz) if dataSz>0 else None
  return (cmd,data)
 
