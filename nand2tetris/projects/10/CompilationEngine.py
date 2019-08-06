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

    while self.tokenizer.keyword() in ["field", "static"]:
      self.CompileClassVarDec()
      self.tokenizer.advance()

    while self.tokenizer.keyword() in ["constructor", "function", "method"]:
      self.CompileSubroutineDec()
      self.tokenizer.advance()

    self.tokenizer.advance()
    self.writeSymbol() # }
    self.writeNewline()

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
      self.writeIdentifier() # varName, should maybe store this?
      self.writeNewline()
      self.tokenizer.advance()

    self.writeSymbol() # ;
    self.writeNewline()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</classVarDec>")
    self.writeNewline()

  def CompileSubroutineDec(self):
    self.outputFile.write(self.indentation+"<subroutineDec>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # constructor | function | method
    self.writeNewline()

    self.tokenizer.advance() # typename
    if self.tokenizer.keyword() in self.types or self.tokenizer.keyword() == "void":
      self.writeKeyword()
    else:
      self.writeIdentifier()
    self.writeNewline()

    self.tokenizer.advance()
    self.tokenizer.writeIdentifier() # subroutineName, should maybe store this?
    self.writeNewline()
    
    self.tokenizer.advance()
    self.writeSymbol() # '('
    self.writeNewline()

    self.tokenizer.advance()
    if self.tokenizer.symbol() != ")":
      self.compileParameterList()

    self.writeSymbol() # ')'
    self.writeNewline()

    self.tokenizer.advance()
    self.compileSubroutineBody()
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</subroutineDec>")
    self.writeNewline()

  def compileParameterList(self):
    self.outputFile.write(self.indentation+"<parameterList>")
    self.writeNewline()
    self.incrementIndentation()

    if self.tokenizer.keyword() in self.types: # typename
      self.writeKeyword()
    else:
      self.writeIdentifier()
    self.writeNewline()

    self.tokenizer.advance()
    self.writeIdentifier() # varName
    self.writeNewline()

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ",":
      self.writeSymbol()
      self.writeNewline() # ,
      self.tokenizer.advance()

      if self.tokenizer.keyword() in self.types: # typename
        self.writeKeyword()
      else:
        self.writeIdentifier()
      self.writeNewline()

      self.tokenizer.advance()
      self.writeIdentifier() # varName
      self.writeNewline()

      self.tokenizer.advance()
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</parameterList>")
    self.writeNewline()

  def compileSubroutineBody(self):
    self.outputFile.write(self.indentation+"<subroutineBody>")
    self.writeNewline()
    self.incrementIndentation()
   
    self.writeSymbol() # '{'
    self.writeNewline()

    self.tokenizer.advance()

    while self.tokenizer.keyword() == "var":
      self.compileVarDec()
      self.tokenizer.advance()

    self.compileStatements()

    self.writeSymbol() # '}'
    self.writeNewline()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</subroutineBody>")
    self.writeNewline()

  def compileVarDec(self):
    self.outputFile.write(self.indentation+"<classVarDec>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # var
    self.writeNewline()
    
    self.tokenizer.advance()
    self.writeKeyword() # type
    self.writeNewline()

    self.tokenizer.advance()
    self.writeIdentifier() # varName
    self.writeNewline()

    self.tokenizer.advance()

    while self.tokenizer.symbol == ",":
      self.writeSymbol() # ,
      self.writeNewline()
      self.tokenizer.advance()
      self.writeIdentifier() # varName
      self.writeNewline()
      self.tokenizer.advance()

    self.writeSymbol()
    self.writeNewline()  
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</classVarDec>")
    self.writeNewline()

  def compileStatements(self):
    self.outputFile.write(self.indentation+"<statements>")
    self.writeNewline()
    self.incrementIndentation()

    while True:
      if self.tokenizer.keyword() == "let":
        self.compileLet()
      elif self.tokenizer.keyword() == "if":
        self.compileIf()
      elif self.tokenizer.keyword() == "while":
        self.compileWhile()
      elif self.tokenizer.keyword() == "do":
        self.compileDo()
      elif self.tokenizer.keyword() == "return":
        self.compileReturn()
      else:
        break
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</statements>")
    self.writeNewline()

  def compileLet(self):
    self.outputFile.write(self.indentation+"<letStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # let
    self.writeNewline()
    self.tokenizer.advance()

    self.writeIdentifier() # varName
    self.writeNewline()
    self.tokenizer.advance()

    if self.tokenizer.symbol() == "[":
      self.tokenizer.writeSymbol() # [
      self.writeNewline()
      self.tokenizer.advance()

      self.compileExpression()

      self.tokenizer.writeSymbol() # ]
      self.writeNewline()
      self.tokenizer.advance()

    self.tokenizer.writeSymbol() # =
    self.writeNewline()
    self.tokenizer.advance()

    self.compileExpression()

    self.tokenizer.writeSymbol() # ;
    self.writeNewline()
    self.tokenizer.advance()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</letStatement>")
    self.writeNewline()
    

  def compileIf(self):
    self.outputFile.write(self.indentation+"<ifStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # if
    self.writeNewline()
    self.tokenizer.advance()
    
    self.writeSymbol() # (
    self.writeNewline()
    self.tokenizer.advance()

    self.compileExpression()

    self.writeSymbol() # )
    self.writeNewline()
    self.tokenizer.advance()

    self.writeSymbol() # {
    self.writeNewline()
    self.tokenizer.advance()

    self.compileStatements()

    self.writeSymbol() # }
    self.writeNewline()
    self.tokenizer.advance()

    if self.tokenizer.keyword() == "else":
      self.writeKeyword() # else
      self.writeNewline()
      self.tokenizer.advance()

      self.writeSymbol() # {
      self.writeNewline()
      self.tokenizer.advance()

      self.compileStatements()

      self.writeSymbol() # }
      self.writeNewline()
      self.tokenizer.advance()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</ifStatement>")
    self.writeNewline()

  def compileWhile(self):
    self.outputFile.write(self.indentation+"<whileStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # while
    self.writeNewline()
    self.tokenizer.advance()

    self.writeSymbol() # (
    self.writeNewline()
    self.tokenizer.advance()

    self.compileExpression()

    self.writeSymbol() # )
    self.writeNewline()
    self.tokenizer.advance()
    
    self.writeSymbol() # {
    self.writeNewline()
    self.tokenizer.advance()

    self.compileStatements()

    self.writeSymbol() # }
    self.writeNewline()
    self.tokenizer.advance()

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</whileStatement>")
    self.writeNewline()

  def compileDo(self):
    self.outputFile.write(self.indentation+"<doStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # do
    self.writeNewline()
    self.tokenizer.advance()

    self.compileSubroutineCall()

    self.writeSymbol() # ;
    self.writeNewline()
    self.tokenizer.advance()
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</doStatement>")
    self.writeNewline()

  def compileReturn(self):
    self.outputFile.write(self.indentation+"<returnStatement>")
    self.writeNewline()
    self.incrementIndentation()
   
    self.writeKeyword() # return
    self.writeNewline()
    self.tokenizer.advance()

    if self.tokenizer.symbol() != ";":
      self.compileExpression()

    self.writeSymbol() # ;
    self.writeNewline()
    self.tokenizer.advance()
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</returnStatement>")
    self.writeNewline()

  def compileExpression(self):
    self.outputFile.write(self.indentation+"<expression>")
    self.writeNewline()
    self.incrementIndentation()
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</expression>")
    self.writeNewline()

  def compileTerm(self):
    pass

  def compileSubroutineCall(self):
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
