# On entering each compile function, the current token should be the unit's starting token
import pdb
import SymbolTable

def binaryOperatorToCommand(operator):
  if operator == "+":
    return VMWriter.Command.ADD
  elif operator ==  "-":
    return VMWriter.Command.SUB
  elif operator == "&":
    return VMWriter.Command.AND
  elif operator == "|":
    return VMWriter.Command.OR
  elif operator == "<":
    return VMWriter.Command.LT
  elif operator == ">":
    return VMWriter.Command.GT
  else:
    print("Invalid BINARY operator!")

def unaryOperatorToCommand(operator):
  if operator == "-":
    return VMWriter.Command.NEG
  elif operator == "~":
    return VMWriter.Command.NOT
  else:
    print("Invalid UNARY operator")
  
def varKindToSegment(kind):
  if kind == SymbolTable.Kind.STATIC:
    return VMWriter.Segment.STATIC
  elif kind == SymbolTable.Kind.FIELD:
    return VMWriter.Segment.THIS
  elif kind == SymbolTable.Kind.ARG:
    return VMWriter.Segment.ARG
  elif kind == SymbolTable.Kind.VAR:
    return VMWriter.Segment.LOCAL

def charXMLify(char):
  if char == "<":
    return "&lt;"
  elif char == ">":
    return "&gt;"
  elif char == "&":
    return "&amp;"
  else:
    return char

class CompilationEngine:
  def __init__(self, tokenizer, outputFilename, vmWriter):
    self.tokenizer = tokenizer
    self.outputFile = open(outputFilename, "w")
    self.vmWriter = vmWriter
    self.indentation = ""
    self.types = ["int", "char", "boolean"]
    self.classType = ""
    self.classLevelST = SymbolTable.SymbolTable()
    self.routineLevelST = SymbolTable.SymbolTable()
    self.ifStatmentIndex = 0
    self.whileStatementIndex = 0
    self.subroutineSTs = []

  def resetRoutineSymbolTables(self):
    self.routineLevelST = SymbolTable.SymbolTable()
    self.subroutineSTs = []

  def findVariable(self, name):
    if self.routineLevelST.find(name):
      st = self.routineLevelST
    elif self.classLevelST.find(name):
      st = self.classLevelST
    else:
      print("var not found")
      return SymbolTable.VariableProperties()
    return SymbolTable.VariableProperties(st.typeOf(name), st.kindOf(name), st.indexOf(name))

  def CompileClass(self):
    self.outputFile.write(self.indentation+"<class>")
    self.writeNewline()
    self.incrementIndentation()
    
    self.writeKeyword() # class

    self.tokenizer.advance()
    self.writeIdentifier() # classname
    self.classType = self.tokenizer.identifier()
   
    self.tokenizer.advance()
    self.writeSymbol() # {

    self.tokenizer.advance()

    while self.tokenizer.keyword() in ["field", "static"]:
      self.CompileClassVarDec()
      self.tokenizer.advance()

    while self.tokenizer.keyword() in ["constructor", "function", "method"]:
      self.CompileSubroutineDec()
      self.tokenizer.advance()

    self.writeSymbol() # }

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</class>")
    self.writeNewline()
     

  def CompileClassVarDec(self):
    self.outputFile.write(self.indentation+"<classVarDec>")
    self.writeNewline()
    self.incrementIndentation()

    varKind = SymbolTable.Kind[self.tokenizer.keyword().upper()]
    self.writeKeyword() # field | static

    self.tokenizer.advance() # typename
    if self.tokenizer.keyword() in self.types:
      varType = self.tokenizer.keyword()
      self.writeKeyword()
    else:
      varType = self.tokenizer.identifier()
      self.writeIdentifier()

    self.tokenizer.advance()
    varName = self.tokenizer.identifier()
    self.writeIdentifier() # varName

    self.classLevelST.define(varName, varType, varKind) # add var declaration to class level ST
    self.writeIdentifierHandling(varName, True, False, False)

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ',':
      self.writeSymbol() # ,
      self.tokenizer.advance()
      self.writeIdentifier() # varName, should maybe store this?
      varName = self.tokenizer.identifier()
      self.classLevelST.define(varName, varType, varKind) # add var declaration to class level ST
      self.writeIdentifierHandling(varName, True, False, False)
      self.tokenizer.advance()

    self.writeSymbol() # ;

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</classVarDec>")
    self.writeNewline()

  def CompileSubroutineDec(self):
    self.outputFile.write(self.indentation+"<subroutineDec>")
    self.writeNewline()
    self.incrementIndentation()

    self.resetRoutineSymbolTables()

    self.writeKeyword() # constructor | function | method

    if self.tokenizer.keyword() == "method":
      self.routineLevelST.define("this", self.classType, SymbolTable.Kind.ARG) # add this var to method level ST 
      self.writeIdentifierHandling("this", True, False, True)

    self.tokenizer.advance() # typename
    if self.tokenizer.keyword() in self.types or self.tokenizer.keyword() == "void":
      self.writeKeyword()
    else:
      self.writeIdentifier()

    self.tokenizer.advance()
    self.writeIdentifier() # subroutineName, should maybe store this?
    
    self.tokenizer.advance()
    self.writeSymbol() # '('

    self.tokenizer.advance()
    self.compileParameterList()

    self.writeSymbol() # ')'

    self.tokenizer.advance()
    self.compileSubroutineBody()
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</subroutineDec>")
    self.writeNewline()

  def compileParameterList(self):
    self.outputFile.write(self.indentation+"<parameterList>")
    self.writeNewline()
    self.incrementIndentation()

    if self.tokenizer.symbol() != ")":

      if self.tokenizer.keyword() in self.types: # typename
        varType = self.tokenizer.keyword()
        self.writeKeyword()
      else:
        varType = self.tokenizer.identifier()
        self.writeIdentifier()

      self.tokenizer.advance()
      varName = self.tokenizer.identifier()
      self.writeIdentifier() # varName

      self.routineLevelST.define(varName, varType, SymbolTable.Kind.ARG)
      self.writeIdentifierHandling(varName, True, False, True)

      self.tokenizer.advance()

      while self.tokenizer.symbol() == ",":
        self.writeSymbol()
        self.tokenizer.advance()

        if self.tokenizer.keyword() in self.types: # typename
          varType = self.tokenizer.keyword()
          self.writeKeyword()
        else:
          varType = self.tokenizer.identifier()
          self.writeIdentifier()

        self.tokenizer.advance()
        varName = self.tokenizer.identifier()
        self.writeIdentifier() # varName

        self.routineLevelST.define(varName, varType, SymbolTable.Kind.ARG)
        self.writeIdentifierHandling(varName, True, False, True)

        self.tokenizer.advance()
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</parameterList>")
    self.writeNewline()

  def compileSubroutineBody(self):
    self.outputFile.write(self.indentation+"<subroutineBody>")
    self.writeNewline()
    self.incrementIndentation()
   
    self.writeSymbol() # '{'

    self.tokenizer.advance()

    while self.tokenizer.keyword() == "var":
      self.compileVarDec()
      self.tokenizer.advance()

    self.compileStatements()

    self.writeSymbol() # '}'

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</subroutineBody>")
    self.writeNewline()

  def compileVarDec(self):
    self.outputFile.write(self.indentation+"<varDec>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # var
    self.tokenizer.advance()
    
    if self.tokenizer.keyword() in self.types: # typename
      varType = self.tokenizer.keyword()
      self.writeKeyword()
    else:
      varType = self.tokenizer.identifier()
      self.writeIdentifier()

    self.tokenizer.advance()
    varName = self.tokenizer.identifier()
    self.writeIdentifier() # varName

    self.routineLevelST.define(varName, varType, SymbolTable.Kind.VAR)
    self.writeIdentifierHandling(varName, True, False, True)

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ",":
      self.writeSymbol() # ,
      self.tokenizer.advance()
      varName = self.tokenizer.identifier()
      self.writeIdentifier() # varName
      self.routineLevelST.define(varName, varType, SymbolTable.Kind.VAR)
      self.writeIdentifierHandling(varName, True, False, True)
      self.tokenizer.advance()

    self.writeSymbol() # ;
    
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</varDec>")
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
    self.tokenizer.advance()

    varName = self.tokenizer.identifier()
    self.writeIdentifierHandling(self.tokenizer.identifier(), False, True, True)

    self.writeIdentifier() # varName
    self.tokenizer.advance()

    if self.tokenizer.symbol() == "[":
      self.writeSymbol() # [
      self.tokenizer.advance()

      self.compileExpression()

      self.writeSymbol() # ]
      self.tokenizer.advance()

    self.writeSymbol() # =
    self.tokenizer.advance()

    self.compileExpression()

    self.writeSymbol() # ;
    self.tokenizer.advance()

    varProperties = self.findVariable(identifier)
    if not varProperties.empty():
      self.vmWriter.writePop(varKindToSegment(varProperties.kind), varProperties.index)

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</letStatement>")
    self.writeNewline()
    

  def compileIf(self):
    self.outputFile.write(self.indentation+"<ifStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # if
    self.tokenizer.advance()
    
    self.writeSymbol() # (
    self.tokenizer.advance()

    self.compileExpression()

    self.writeSymbol() # )
    self.tokenizer.advance()

    self.vmWriter.writeArithmetic(VMWriter.Command.NOT)
    self.vmWriter.writeIf("IF_LABEL_1"+"_"+self.classType+"_"+str(self.ifStatementIndex))

    self.writeSymbol() # {
    self.tokenizer.advance()

    self.compileStatements()

    self.writeSymbol() # }
    self.tokenizer.advance()

    self.vmWriter.writeGoto("IF_LABEL_2"+"_"+self.classType+"_"+str(self.ifStatementIndex))
    self.vmWriter.writeLabel("IF_LABEL_1"+"_"+self.classType+"_"+str(self.ifStatementIndex))

    if self.tokenizer.keyword() == "else":
      self.writeKeyword() # else
      self.tokenizer.advance()

      self.writeSymbol() # {
      self.tokenizer.advance()


      self.compileStatements()

      self.writeSymbol() # }
      self.tokenizer.advance()

    self.vmWriter.writeLabel("IF_LABEL_2"+"_"+self.classType+"_"+str(self.ifStatementIndex))
    self.ifStatementIndex += 1

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</ifStatement>")
    self.writeNewline()

  def compileWhile(self):
    self.outputFile.write(self.indentation+"<whileStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # while
    self.tokenizer.advance()

    self.writeSymbol() # (
    self.tokenizer.advance()

    self.vmWriter.writeLabel("WHILE_LABEL_1"+"_"+self.classType+"_"+str(self.whileStatementIndex))

    self.compileExpression()

    self.writeSymbol() # )
    self.tokenizer.advance()
    
    self.writeSymbol() # {
    self.tokenizer.advance()

    self.vmWriter.writeArithmetic(VMWriter.Command.NOT)
    self.vmWriter.writeIf("WHILE_LABEL_2"+"_"+self.classType+"_"+str(self.whileStatementIndex))

    self.compileStatements()

    self.writeSymbol() # }
    self.tokenizer.advance()

    self.vmWriter.writeGoto("WHILE_LABEL_1"+"_"+self.classType+"_"+str(self.whileStatementIndex))
    self.vmWriter.writeLabel("WHILE_LABEL_2"+"_"+self.classType+"_"+str(self.whileStatementIndex))

    self.whileStatementIndex += 1

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</whileStatement>")
    self.writeNewline()

  def compileDo(self):
    self.outputFile.write(self.indentation+"<doStatement>")
    self.writeNewline()
    self.incrementIndentation()

    self.writeKeyword() # do
    self.tokenizer.advance()

    self.compileSubroutineCall()

    self.writeSymbol() # ;
    self.tokenizer.advance()
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</doStatement>")
    self.writeNewline()

  def compileReturn(self):
    self.outputFile.write(self.indentation+"<returnStatement>")
    self.writeNewline()
    self.incrementIndentation()
   
    self.writeKeyword() # return
    self.tokenizer.advance()

    if self.tokenizer.symbol() != ";":
      self.compileExpression()

    self.writeSymbol() # ;
    self.tokenizer.advance()

    self.vmWriter.writeReturn()
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</returnStatement>")
    self.writeNewline()

  def compileExpression(self):
    self.outputFile.write(self.indentation+"<expression>")
    self.writeNewline()
    self.incrementIndentation()

    self.compileTerm()

    while self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">"]:
      operator = self.tokenizer.symbol()
      self.writeSymbol()
      self.tokenizer.advance()
      self.compileTerm()
      if operator == "*":
        self.vmWriter.writeCall("Math.multiply", 2)
      elif operator == "/":
        self.vmWriter.writeCall("Math.divide", 2)
      else:
        self.vmWriter.writeArithmetic(binaryOperatorToCommand(operator))
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</expression>")
    self.writeNewline()

  def compileTerm(self):
    self.outputFile.write(self.indentation+"<term>")
    self.writeNewline()
    self.incrementIndentation()

    if self.tokenizer.intVal(): # int const

      self.vmWriter.writePush(VMWriter.Segment.CONST, self.tokenizer.intVal())

      self.writeIntegerConstant()
      self.tokenizer.advance()
    elif self.tokenizer.stringVal(): # string const
     
      string = self.tokenizer.stringVal()
      self.vmWriter.writeCall("String.new", str(len(string)))
      for c in string:
        self.vmWriter.writeCall("String.append", str(ord(c)) 
 
      self.writeStringConstant()
      self.tokenizer.advance()
    elif self.tokenizer.keyword() in ["true", "false", "null", "this"]: # keyword const

      if self.tokenizer.keyword() == "true":
        self.vmWriter.writePush(VMWriter.Segment.CONST, str(1))
        self.vmWriter.writeArithmetic(VMWriter.Command.NEG)
      elif self.tokenizer.keyword() in ["false, null"]:
        self.vmWriter.writePush(VMWriter.Segment.CONST, str(0))

      self.writeKeyword()
      self.tokenizer.advance()
    elif self.tokenizer.identifier(): # varName

      varName = self.tokenizer.identifier()
      varProperties = self.findVariable(varName)
      if not varProperties.empty():
        self.vmWriter.writePush(varKindToSegment(varProperties.kind), varProperties.index)

      self.writeIdentifier()
      self.writeIdentifierHandling(self.tokenizer.identifier(), False, True, True)
      self.tokenizer.advance()
      if self.tokenizer.symbol() == '[': # varName[expression]
        self.writeSymbol() # [
        self.tokenizer.advance()
        self.compileExpression()
        self.writeSymbol() # ]
        self.tokenizer.advance()
      elif self.tokenizer.symbol() == '.':
        self.writeSymbol() # .
        self.tokenizer.advance()
        self.writeIdentifier() # subroutine name
        self.tokenizer.advance()
        self.writeSymbol() # (
        self.tokenizer.advance()
        nArgs = self.compileExpressionList()
        self.writeSymbol() # )
        self.tokenizer.advance()
        self.vmWriter.writeCall(routineName, nArgs+1) # +1 for the object as first arg
      elif self.tokenizer.symbol() == '(':
        self.writeSymbol() # (
        self.tokenizer.advance()
        nArgs = self.compileExpressionList()
        self.writeSymbol() # )
        self.tokenizer.advance() 
        self.vmWriter.writeCall(routineName, nArgs)
    elif self.tokenizer.symbol() == "(": # (expression)
      self.writeSymbol() # (
      self.tokenizer.advance()
      self.compileExpression()
      self.writeSymbol() # )
      self.tokenizer.advance()
    elif self.tokenizer.symbol() in ["-", "~"]: # unaryOp termi
      
      unaryOp = self.tokenizer.symbol()

      self.writeSymbol()
      self.tokenizer.advance()
      self.compileTerm()

      self.vmWriter.writeArithmetic(unaryOperatorToCommand(unaryOp))
    else: # subroutineCall
      print("Should not come here")
 
    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</term>")
    self.writeNewline()

  def compileSubroutineCall(self):
    self.writeIdentifier()
    identifier = self.tokenizer.identifier()
    self.tokenizer.advance()

    methodCall = False

    if self.tokenizer.symbol() == ".":
      if identifier != self.classType: # varName.subroutineName
        varProperties = self.findVariable(identifier)
        if not varProperties.empty():
          self.vmWriter.writePush(varKindToSegment(varProperties.kind), varProperties.index)
        self.writeIdentifierHandling(identifier, False, True, True)
        methodCall = True
      self.writeSymbol() # .
      self.tokenizer.advance()
      routineName = self.tokenizer.identifier()
      self.writeIdentifier()
      self.tokenizer.advance()
    else:
      routineName = identifier
      

    self.writeSymbol() # (
    self.tokenizer.advance()
   
    nArgs = self.compileExpressionList()
    if methodCall:
      nArgs += 1

    self.writeSymbol() # )
    self.tokenizer.advance()

    self.vmWriter.writeCall(routineName, nArgs)
    
  def compileExpressionList(self):
    self.outputFile.write(self.indentation+"<expressionList>")
    self.writeNewline()
    self.incrementIndentation()

    numExpressions = 0

    if self.tokenizer.symbol() != ")": 
      self.compileExpression()

      while self.tokenizer.symbol() == ",":
        #pdb.set_trace()
        self.writeSymbol()
        self.tokenizer.advance()

        self.compileExpression()

        numExpressions += 1

    self.decrementIndentation()
    self.outputFile.write(self.indentation+"</expressionList>")
    self.writeNewline()

    return numExpressions

  def writeNewline(self):
    self.outputFile.write("\r\n")

  def writeKeyword(self):
    self.outputFile.write(self.indentation+"<keyword> "+self.tokenizer.keyword()+" </keyword>")
    self.writeNewline()
    
  def writeIdentifier(self):
    self.outputFile.write(self.indentation+"<identifier> "+self.tokenizer.identifier()+" </identifier>")
    self.writeNewline()
  
  def writeSymbol(self):  
    self.outputFile.write(self.indentation+"<symbol> "+charXMLify(self.tokenizer.symbol())+" </symbol>")
    self.writeNewline()

  def writeIntegerConstant(self):
    self.outputFile.write(self.indentation+"<integerConstant> "+self.tokenizer.intVal()+" </integerConstant>")
    self.writeNewline()

  def writeStringConstant(self): 
    self.outputFile.write(self.indentation+"<stringConstant> "+self.tokenizer.stringVal()+" </stringConstant>")
    self.writeNewline()

  def writeIdentifierHandling(self, name, defined, used, routineNotClass=True):
    if defined:
      if routineNotClass:
        self.writeRoutineIdentifierHandling(self.routineLevelST.kindOf(name), self.routineLevelST.indexOf(name), defined, used)
      else:
        self.writeClassIdentifierHandling(self.classLevelST.kindOf(name), self.classLevelST.indexOf(name), defined, used) 
    else:
      if self.routineLevelST.find(name):
        self.writeRoutineIdentifierHandling(self.routineLevelST.kindOf(name), self.routineLevelST.indexOf(name), defined, used)
      elif self.classLevelST.find(name):
        self.writeClassIdentifierHandling(self.classLevelST.kindOf(name), self.classLevelST.indexOf(name), defined, used) 
        

  def writeClassIdentifierHandling(self, category, index, defined, used):
    self.outputFile.write(self.indentation+"<CLASS IDHANDLING> Cat: "+str(category)+" index: "+str(index)+" defined: "+str(defined)+" used: "+str(used)+" </CLASS IDHANDLING>")
    self.writeNewline() 

  def writeRoutineIdentifierHandling(self, category, index, defined, used):
    self.outputFile.write(self.indentation+"<ROUTINE IDHANDLING> Cat: "+str(category)+" index: "+str(index)+" defined: "+str(defined)+" used: "+str(used)+" </ROUTINE IDHANDLING>")
    self.writeNewline() 

  def incrementIndentation(self):
    self.indentation += "  "

  def decrementIndentation(self):
    self.indentation = self.indentation[:-2]
