

class VMWriter:
  def __init__(self, outputFilename):
    self.outputFile = open(outputFilename, 'w')

  def writePush(self):
    pass

  def writePop(self):
    pass

  def writeArithmetic(self):
    pass

  def writeLabel(self):
    pass

  def writeGoto(self):
    pass

  def writeIf(self):
    pass

  def writeCall(self):
    pass

  def writeFunction(self):
    pass

  def writeReturn(self):
    pass

  def close(self):
    self.outputFile.close()
