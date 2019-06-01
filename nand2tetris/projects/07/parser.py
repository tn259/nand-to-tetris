import command_types
import pdb

class Parser:
  def __init__(self, filename):
    self.fileHandle = open(filename, "r")
    self.currentLine = None


  def hasMoreCommands(self):
    return self.currentLine != ''


  def advance(self):
    while True:
      self.currentLine = self.fileHandle.readline()
      if not (self.currentLine == "\r\n" or self.currentLine.startswith("//")): # Skip newlines and comments
        commentPos = self.currentLine.find("//")
        if commentPos == -1:
          self.currentLine = self.currentLine[:-2].strip(' ') # Strip off \r\n and whitespace
        else:
          self.currentLine = self.currentLine[:commentPos].strip(' ') # Strip off end comment and whitespace
        break

  
  def commandType(self):
    command = self.currentLine.split(' ')[0]
    if command == "push":
      return command_types.C_PUSH
    elif command == "pop":
      return command_types.C_POP
    elif command == "label":
      return command_types.C_LABEL
    elif command == "goto":
      return command_types.C_GOTO
    elif command == "if":
      return command_types.C_IF
    elif command == "function":
      return command_types.C_FUNTION
    elif command == "return":
      return command_types.C_RETURN
    elif command == "call":
      return command_types.C_CALL
    elif command == "add" or command == "sub" or command == "neg" or command == "eq" or command == "gt" or command == "lt"\
         or command == "and" or command == "or" or command == "not":
      return command_types.C_ARITHMETIC
    else:
      return None

  def arg1(self):
    commandType = self.commandType()
    if commandType == command_types.C_RETURN or commandType == None:
      return None
    elif commandType == command_types.C_ARITHMETIC:
      return self.currentLine.split(' ')[0]
    else:
      return self.currentLine.split(' ')[1]

  def arg2(self):
    commandType = self.commandType()
    if commandType == command_types.C_PUSH or commandType == command_types.C_POP or commandType == command_types.C_FUNCTION or commandType == command_types.C_CALL:
      return self.currentLine.split(' ')[2]
    else:
      return None
