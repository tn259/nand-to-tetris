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
    if self.currentLine[0] == "@":
      return command_types.A_COMMAND
    elif self.currentLine.startswith('(') and self.currentLine.endswith(')'):
      return command_types.L_COMMAND
    elif "=" in self.currentLine or ";" in self.currentLine:
      return command_types.C_COMMAND
    else:
      return None


  def symbol(self):
    commandType = self.commandType()
    if commandType == command_types.L_COMMAND: # Strip off parentheses
      return self.currentLine[1:-1]
    elif commandType == command_types.A_COMMAND: # Strip off leading '@'
      return self.currentLine[1:]
    else:
      return None


  def dest(self):
    commandType = self.commandType()
    if commandType == command_types.C_COMMAND:
      if '=' in self.currentLine:
        return self.currentLine[0:self.currentLine.find('=')]
      else:
        return ""
    else:
      return None


  def comp(self):
    commandType = self.commandType()
    if commandType == command_types.C_COMMAND:
      startIndex = 0
      if '=' in self.currentLine:
        return self.currentLine[self.currentLine.find('=')+1:]
      elif ';' in self.currentLine:
        return self.currentLine[:self.currentLine.find(';')]
    else:
      return None


  def jump(self):
    commandType = self.commandType()
    if commandType == command_types.C_COMMAND:
      if ";" in self.currentLine:
        return self.currentLine[self.currentLine.find(';')+1:]
      else:
        return ""
    else:
      return None    
