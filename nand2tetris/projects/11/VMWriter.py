import Enum from enum

class Segment(Enum):
  CONST = 0
  ARG = 1
  LOCAL = 2
  STATIC = 3
  THIS = 4
  THAT = 5
  POINTER = 6
  TEMP = 7
  NONE = 8

class Command(Enum):
  ADD = 0
  SUB = 1
  NEG = 2
  EQ = 3
  GT = 4
  LT = 5
  AND = 6
  OR = 7
  NOT = 8

class VMWriter:
  def __init__(self, outputFilename):
    self.outputFile = open(outputFilename, 'w')

  def writePush(self, segment, index):
    if segment != Segment.NONE
      self.outputFile.write("push "+segment.name.lower()+" "+str(index))
    else:
      self.outputFile.write("push "+str(index))
    self.writeNewline()

  def writePop(self, segment, index):
    self.outputFile.write("pop "+segment.name.lower()+" "+str(index))
    self.writeNewline()

  def writeArithmetic(self, command):
    self.outputFile.write(command.name.lower())
    self.writeNewline()

  def writeLabel(self, label):
    self.outputFile.write("label "+label)
    self.writeNewline()

  def writeGoto(self, label):
    self.outputFile.write("goto "+label)
    self.writeNewline()

  def writeIf(self, label):
    self.outputFile.write("if-goto "+label)
    self.writeNewline()

  def writeCall(self, name, nArgs):
    self.outputFile.write("call "+name+" "+str(nArgs))
    self.writeNewline()

  def writeFunction(self, name, nLocals):
    self.outputFile.write("function "+name+" "+str(nLocals))
    self.writeNewline()

  def writeReturn(self):
    self.outputFile.write("return")
    self.writeNewline()

  def writeNewline(self):
    self.outputFile.write("\r\n")

  def close(self):
    self.outputFile.close()
