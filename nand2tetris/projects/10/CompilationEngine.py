# On entering each compile function, the current token should be the unit's starting token

class CompilationEngine:
  def __init__(self, tokenizer, outputFilename):
    self.tokenizer = tokenizer
    self.outputFile = open(outputFilename, "w")
    self.indentation = ""
    self.types = ["int", "char", "boolean"]

  def CompileClass(self):
    self.outputFile.write(self.indentation+"<class>")
    self.writeNewline()
    self.incrementIndentation()
     
    self.writeKeyword() # class
    self.writeNewline()

    self.tokenizer.advance()
    self.writeIdentifier() # classname
    self.writeNewline()
   
    self.tokenizer.advance()
    self.writeSymbol() # {
    self.writeNewline()

    self.tokenizer.advance()

    while self.tokenizer.keyword() == "field" or self.tokenizer.keyword() == "static":
      self.CompileClassVarDec()
      self.tokenizer.advance()

    



    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</class>")
     

  def CompileClassVarDec(self):
    self.outputFile.write(self.indentation+"<classVarDec>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # field | static
    self.writeNewline()

    self.tokenizer.advance() # typename
    if self.tokenizer.keyword() in self.types:
      self.writeKeyword()
    else:
      self.writeIdentifier()
    self.writeNewline()

    self.tokenizer.advance()
    self.writeIdentifier() # varName
    self.writeNewline()

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ',':
      self.writeSymbol()
      self.writeNewline() # ,
      self.tokenizer.advance()
      self.writeIdentifier() # varName
      self.writeNewline()
      self.tokenizer.advance()

    self.writeSymbol() # ;
    self.writeNewline()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</classVarDec>")
    self.writeNewline()

  def ComplileSubroutineDec(self):
    pass

  def compileParameterList(self):
    pass

  def compileSubroutineBody(self):
    pass

  def compileVarDec(self):
    pass

  def compileStatements(self):
    pass

  def compileLet(self):
    pass

  def compileIf(self):
    pass

  def compileDo(self):
    pass

  def compileReturn(self):
    pass

  def writeNewline(self):
    self.outputFile.write("\r\n")

  def writeKeyword(self):
    self.outputFile.write(self.indentation+"<keyword> "+self.tokenizer.keyword()+" </keyword>")
    
  def writeIdentifier(self):
    self.outputFile.write(self.indentation+"<identifier> "+self.tokenizer.identifier()+" </identifier>")
  
  def writeSymbol(self):  
    self.outputFile.write(self.indentation+"<symbol> "+self.tokenizer.symbol()+" </symbol>")

  def incrementIndentation(self):
    self.indentation += "  "

  def decrementIndentation(self):
    self.indentation = self.indentation[:-2]
