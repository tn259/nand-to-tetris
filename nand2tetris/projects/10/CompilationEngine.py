
class ComplilationEngine:
  def __init__(self, tokenizer, outputFilename):
    self.tokenizer = tokenizer
    self.outputFile = open(outputFilename, "w")
    self.indentation = ""

  def CompileClass(self):
    self.outputFile.write(self.indentation+"<class>")
    self.writeNewline()
    self.incrementIndentation() 
    self.t.advance()
    

  def CompileClassVarDec(self):

  def ComplileSubroutineDec(self):

  def compileParameterList(self):

  def compileSubroutineBody(self):

  def compileVarDec(self):

  def compileStatements(self):

  def compileLet(self):

  def compileIf(self):

  def compileDo(self):

  def compileReturn(self):

  def writeNewline(self):
    self.outputFile.write("\r\n")

  def incrementIndentation(self):
    self.indentation + "  "

  def decrementIndentation(self):
    self.indentation = self.indentation[:-2]
