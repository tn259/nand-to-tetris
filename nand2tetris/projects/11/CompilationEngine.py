# On entering each compile function, the current token should be the unit's starting token
import pdb
import SymbolTable
import VMWriter
from enum import Enum

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
    return VMWriter.Segment.ARGUMENT
  elif kind == SymbolTable.Kind.VAR:
    return VMWriter.Segment.LOCAL

class SubroutineType(Enum):
  CTOR = 0
  METHOD = 1
  FUNCTION = 2
  NONE = 3

class CompilationEngine:
  def __init__(self, tokenizer, vmWriter):
    self.tokenizer = tokenizer
    self.vmWriter = vmWriter
    self.types = ["int", "char", "boolean"]
    self.className = ""
    self.classLevelST = SymbolTable.SymbolTable()
    self.routineLevelST = SymbolTable.SymbolTable()
    self.ifStatementIndex = 0
    self.whileStatementIndex = 0
    self.currentSubroutineDecType = SubroutineType.NONE
    self.currentSubroutineDecName = ""
    self.currentSubroutineDecReturnsVoid = False
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
      return SymbolTable.VarProperties()
    return SymbolTable.VarProperties(st.typeOf(name), st.kindOf(name), st.indexOf(name))


  def CompileClass(self):
    # tokenizer starts by holding keyword "class"
    self.tokenizer.advance() 
    # classname
    self.className = self.tokenizer.identifier()

    pdb.set_trace()
   
    self.tokenizer.advance()
    # '{'

    self.tokenizer.advance()

    while self.tokenizer.keyword() in ["field", "static"]:
      self.CompileClassVarDec()
      self.tokenizer.advance()

    while self.tokenizer.keyword() in ["constructor", "function", "method"]:
      self.CompileSubroutineDec()
      self.tokenizer.advance()

    # '}'


  def CompileClassVarDec(self):
    # 'field' | 'static'
    varKind = SymbolTable.Kind[self.tokenizer.keyword().upper()]

    self.tokenizer.advance() 
    # typename
    if self.tokenizer.keyword() in self.types:
      varType = self.tokenizer.keyword()
    else:
      varType = self.tokenizer.identifier()

    self.tokenizer.advance() 
    # varName
    varName = self.tokenizer.identifier()

    self.classLevelST.define(varName, varType, varKind) # add var declaration to class level ST

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ',':
      self.tokenizer.advance() 
      # varName
      varName = self.tokenizer.identifier()
      self.classLevelST.define(varName, varType, varKind) # add var declaration to class level ST
      self.tokenizer.advance()

    # ';'


  def CompileSubroutineDec(self):
    self.resetRoutineSymbolTables()

    if self.tokenizer.keyword() == "method":
      self.currentSubroutineDecType = SubroutineType.METHOD
      self.routineLevelST.define("this", self.className, SymbolTable.Kind.ARG) # add this var to method level ST 
    elif self.tokenizer.keyword() == "constructor":
      self.currentSubroutineDecType = SubroutineType.CTOR
    elif self.tokenizer.keyword() == "function":
      self.currentSubroutineDecType = SubroutineType.FUNCTION

    self.tokenizer.advance() 
    # typename
    if self.tokenizer.keyword() == "void":
      self.currentSubroutineDecReturnsVoid = True

    self.tokenizer.advance() 
    # subroutineName

    self.currentSubroutineDecName = self.tokenizer.identifier()
    
    self.tokenizer.advance() 

    # '('

    self.tokenizer.advance()
    nParams = self.compileParameterList()

    # ')'

    self.tokenizer.advance()
    self.compileSubroutineBody()
    
    # reset subroutine members  
    self.currentSubroutineDecType = SubroutineType.NONE
    self.currentSubroutineDecName = ""
    self.currentSubroutineDecReturnsVoid = False
    

  def compileParameterList(self):

    nParams = 0

    if self.tokenizer.symbol() != ")":

      if self.tokenizer.keyword() in self.types: # typename
        varType = self.tokenizer.keyword()
      else:
        varType = self.tokenizer.identifier()

      self.tokenizer.advance()
      varName = self.tokenizer.identifier()

      self.routineLevelST.define(varName, varType, SymbolTable.Kind.ARG)

      self.tokenizer.advance()

      nParams += 1

      while self.tokenizer.symbol() == ",":
        self.tokenizer.advance()

        if self.tokenizer.keyword() in self.types: # typename
          varType = self.tokenizer.keyword()
        else:
          varType = self.tokenizer.identifier()

        self.tokenizer.advance()
        varName = self.tokenizer.identifier()

        self.routineLevelST.define(varName, varType, SymbolTable.Kind.ARG)

        self.tokenizer.advance()

        nParams += 1
    
    return nParams


  def compileSubroutineBody(self):
    # '{'

    self.tokenizer.advance()

    nLocals = 0
    while self.tokenizer.keyword() == "var":
      self.compileVarDec()
      self.tokenizer.advance()
      nLocals += 1

    self.vmWriter.writeFunction(self.className+"."+self.currentSubroutineDecName, nLocals)

    if self.currentSubroutineDecType == SubroutineType.CTOR:
      self.vmWriter.writePush(VMWriter.Segment.NONE, nParams)
      self.vmWriter.writeCall("Memory.alloc", 1)
      self.vmWriter.writePop(VMWriter.Segment.POINTER, 0)
    elif self.currentSubroutineDecType == SubroutineType.METHOD:
      self.vmWriter.writePush(VMWriter.Segment.ARGUMENT, 0)
      self.vmWriter.writePop(VMWriter.Segment.POINTER, 0)

    self.compileStatements()

    # '}'


  def compileVarDec(self):
    # 'var'
    self.tokenizer.advance()
    
    if self.tokenizer.keyword() in self.types: # typename
      varType = self.tokenizer.keyword()
    else:
      varType = self.tokenizer.identifier()

    self.tokenizer.advance()
    varName = self.tokenizer.identifier()
    self.routineLevelST.define(varName, varType, SymbolTable.Kind.VAR)

    self.tokenizer.advance()

    while self.tokenizer.symbol() == ",":
      self.tokenizer.advance()
      varName = self.tokenizer.identifier()
      self.routineLevelST.define(varName, varType, SymbolTable.Kind.VAR)

      self.tokenizer.advance()

    # ';'
    

  def compileStatements(self):
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
    

  def compileLet(self):
    # 'let'
    self.tokenizer.advance()
    varName = self.tokenizer.identifier()

    self.tokenizer.advance()

    arrayAccess = False

    if self.tokenizer.symbol() == "[":
      arrayAccess = True

      self.vmWriter.writePush(VMWriter.Segment.NONE, varName)

      # '['
      self.tokenizer.advance()

      self.compileExpression()

      self.vmWriter.writeArithmetic(VMWriter.Command.ADD)

      # ']'
      self.tokenizer.advance()

    # '='
    self.tokenizer.advance()

    self.compileExpression()

    # ';'
    self.tokenizer.advance()

    if arrayAccess:
      self.vmWriter.writePop(VMWriter.Segment.TEMP, 0)
      self.vmWriter.writePop(VMWriter.Segment.POINTER, 1)
      self.vmWriter.writePush(VMWriter.Segment.TEMP, 0)
      self.vmWriter.writePop(VMWriter.Segment.THAT, 0)
    else:
      varProperties = self.findVariable(varName)
      if not varProperties.empty():
        self.vmWriter.writePop(varKindToSegment(varProperties.kind), varProperties.index)


  def compileIf(self):
    # 'if'

    self.tokenizer.advance()
    # '('

    self.tokenizer.advance()
    self.compileExpression()
    # ')'

    self.tokenizer.advance()

    self.vmWriter.writeArithmetic(VMWriter.Command.NOT)
    self.vmWriter.writeIf("IF_LABEL_1"+"_"+self.className+"_"+str(self.ifStatementIndex))
    # '{'

    self.tokenizer.advance()
    self.compileStatements()
    # '}'

    self.tokenizer.advance()

    self.vmWriter.writeGoto("IF_LABEL_2"+"_"+self.className+"_"+str(self.ifStatementIndex))
    self.vmWriter.writeLabel("IF_LABEL_1"+"_"+self.className+"_"+str(self.ifStatementIndex))

    if self.tokenizer.keyword() == "else":
      # 'else'

      self.tokenizer.advance()
      # '{'

      self.tokenizer.advance()
      self.compileStatements()
      # '}'

      self.tokenizer.advance()

    self.vmWriter.writeLabel("IF_LABEL_2"+"_"+self.className+"_"+str(self.ifStatementIndex))
    self.ifStatementIndex += 1


  def compileWhile(self):
    # 'while'

    self.tokenizer.advance()
    # '('

    self.tokenizer.advance()

    self.vmWriter.writeLabel("WHILE_LABEL_1"+"_"+self.className+"_"+str(self.whileStatementIndex))

    self.compileExpression()

    # ')'

    self.tokenizer.advance()
    # '{'

    self.tokenizer.advance()

    self.vmWriter.writeArithmetic(VMWriter.Command.NOT)
    self.vmWriter.writeIf("WHILE_LABEL_2"+"_"+self.className+"_"+str(self.whileStatementIndex))

    self.compileStatements()
    # '}'

    self.tokenizer.advance()

    self.vmWriter.writeGoto("WHILE_LABEL_1"+"_"+self.className+"_"+str(self.whileStatementIndex))
    self.vmWriter.writeLabel("WHILE_LABEL_2"+"_"+self.className+"_"+str(self.whileStatementIndex))

    self.whileStatementIndex += 1


  def compileDo(self):
    # 'do'

    self.tokenizer.advance()

    self.compileSubroutineCall()

    self.vmWriter.writePop(VMWriter.Segment.TEMP, 0) # assume do statements always call void routines

    # ';'

    self.tokenizer.advance()

 
  def compileReturn(self):
    # 'return'

    self.tokenizer.advance()

    if self.tokenizer.symbol() != ";":
      self.compileExpression()

    # ;

    self.tokenizer.advance()

    if self.currentSubroutineDecType == SubroutineType.CTOR:
      self.vmWriter.writePush(VMWriter.Segment.POINTER, 0) # returns this
    elif self.currentSubroutineDecReturnsVoid:
      self.vmWriter.writePush(VMWriter.Segment.CONSTANT, 0) # ignore return value for void

    self.vmWriter.writeReturn()

 
  def compileExpression(self):
    self.compileTerm()

    while self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">"]:
      operator = self.tokenizer.symbol()
      self.tokenizer.advance()
      self.compileTerm()
      if operator == "*":
        self.vmWriter.writeCall("Math.multiply", 2)
      elif operator == "/":
        self.vmWriter.writeCall("Math.divide", 2)
      else:
        self.vmWriter.writeArithmetic(binaryOperatorToCommand(operator))
 

  def compileTerm(self):

    if self.tokenizer.intVal(): # int const
      self.vmWriter.writePush(VMWriter.Segment.CONSTANT, self.tokenizer.intVal())
      self.tokenizer.advance()

    elif self.tokenizer.stringVal(): # string const
      string = self.tokenizer.stringVal()
      self.vmWriter.writeCall("String.new", str(len(string)))
      for c in string:
        self.vmWriter.writeCall("String.appendChar", str(ord(c))) 
      self.tokenizer.advance()

    elif self.tokenizer.keyword() in ["true", "false", "null", "this"]: # keyword const
      if self.tokenizer.keyword() == "true":
        self.vmWriter.writePush(VMWriter.Segment.CONSTANT, str(1))
        self.vmWriter.writeArithmetic(VMWriter.Command.NEG)
      elif self.tokenizer.keyword() in ["false, null"]:
        self.vmWriter.writePush(VMWriter.Segment.CONSTANT, str(0))
      elif self.tokenizer.keyword() == "this":
        self.vmWriter.writePush(VMWriter.Segment.ARGUMENT, str(0)) # 'this' in routine
      self.tokenizer.advance()

    elif self.tokenizer.identifier(): # varName
      identifier = self.tokenizer.identifier()
      varProperties = self.findVariable(identifier)
      if not varProperties.empty():
        self.vmWriter.writePush(varKindToSegment(varProperties.kind), varProperties.index)
      self.tokenizer.advance()

      if self.tokenizer.symbol() == '[': # varName[expression]
        # '['
        self.tokenizer.advance()

        self.compileExpression()
        self.vmWriter.writeArithmetic(VMWriter.Command.ADD)
        self.vmWriter.writePop(VMWriter.Segment.POINTER, 1)
        self.vmWriter.writePush(VMWriter.Segment.THAT, 0)
        # ']'

        self.tokenizer.advance()

      elif self.tokenizer.symbol() == '.':
        # '.'
        self.tokenizer.advance()

        methodCall = False
        if not varProperties.empty():
          methodCall = True
          routineName = varProperties.typeOf(identifier)+"."+self.tokenizer.identifier()
        else:
          routineName = identifier+"."+self.tokenizer.identifier()  

        self.tokenizer.advance()
        # '('
        self.tokenizer.advance()
        nArgs = self.compileExpressionList()
        # ')'
        self.tokenizer.advance()

        if methodCall: # implicit this argument
          nArgs += 1

        self.vmWriter.writeCall(routineName, nArgs)

      elif self.tokenizer.symbol() == '(': # assume private method call
        routineName = identifier
        # '('
        self.tokenizer.advance()
        nArgs = self.compileExpressionList()
        # ')'
        self.tokenizer.advance() 
        self.vmWriter.writeCall(self.className+"."+routineName, nArgs+1)

    elif self.tokenizer.symbol() == "(": # (expression)
      # '('
      self.tokenizer.advance()
      self.compileExpression()
      # ')'
      self.tokenizer.advance()

    elif self.tokenizer.symbol() in ["-", "~"]: # unaryOp 
      
      unaryOp = self.tokenizer.symbol()

      self.tokenizer.advance()
      self.compileTerm()

      self.vmWriter.writeArithmetic(unaryOperatorToCommand(unaryOp))

    else: # subroutineCall
      print("Should not come here")
 

  def compileSubroutineCall(self):
    identifier = self.tokenizer.identifier()
    self.tokenizer.advance()
    
    methodCall = False

    if self.tokenizer.symbol() == ".":
      varProperties = self.findVariable(identifier)
      if not varProperties.empty():
        self.vmWriter.writePush(varKindToSegment(varProperties.kind), varProperties.index)
        methodCall = True

      # '.'
      self.tokenizer.advance()
      
      if not varProperties.empty(): # varName.subroutineName
        routineName = varProperties.typeOf(identifier)+"."+self.tokenizer.identifier()
      else: # ctor 
        routineName = identifier+"."+self.tokenizer.identifier()

      self.tokenizer.advance()

    else:
      routineName = self.className+"."+identifier # straight subroutine call with no '.' assume private method call
      methodCall = True
      
    # '('

    self.tokenizer.advance()
   
    nArgs = self.compileExpressionList()
    if methodCall:
      nArgs += 1

    # ')'

    self.tokenizer.advance()

    self.vmWriter.writeCall(routineName, nArgs)
    
  def compileExpressionList(self):
    numExpressions = 0

    if self.tokenizer.symbol() != ")": 
      self.compileExpression()
      numExpressions += 1

      while self.tokenizer.symbol() == ",":
        #pdb.set_trace()
        self.tokenizer.advance()

        self.compileExpression()
        numExpressions += 1

    return numExpressions

