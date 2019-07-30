from enum import Enum
import re
import pdb

class TokenType(Enum):
  KEYWORD = 1
  SYMBOL = 2
  IDENTIFIER = 3
  INT_CONST = 4
  STRING_CONST = 5

def Keywords():
  return [
    "CLASS",
    "METHOD",
    "FUNCTION",
    "CONSTRUCTOR",
    "INT",
    "BOOLEAN",
    "CHAR",
    "VOID",
    "VAR",
    "STATIC",
    "FIELD",
    "LET",
    "DO",
    "IF",
    "ELSE",
    "WHILE",
    "RETURN",
    "TRUE",
    "FALSE",
    "NULL",
    "THIS"]

def Symbols():
  return [
    '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'
  ]


class Tokenizer:
  def __init__(self, inputJackFile):
    self.inFileLines = open(inputJackFile, 'r').readlines()
    self.currentToken = None
    self.currentLineIdx = 0
    self.currentLine = self.inFileLines[self.currentLineIdx]
    self.currentTokenStartOffset = 0

  def hasMoreTokens(self):
    return self.currentLineIdx < len(self.inFileLines)
    
  def nextLine(self):
    self.currentLineIdx += 1
    if self.hasMoreTokens():
      self.currentLine = self.inFileLines[self.currentLineIdx]
      self.currentTokenStartOffset = 0
    else:
      self.currentLine = None
      

  def nextToken(self):
    # Process Line
    tokenEndOffset = self.currentTokenStartOffset + 1
    while self.currentLine != None and tokenEndOffset < len(self.currentLine):
      s = self.currentLine[self.currentTokenStartOffset:tokenEndOffset]
      endChar = self.currentLine[tokenEndOffset]
      #pdb.set_trace()
      if len(s) == 1:
        if s in ["\t", "\r", " "]: # Skip over tabs, CR and spaces
          self.currentTokenStartOffset += 1
          tokenEndOffset += 1
        elif s == "\"": # string const find closing " and return update offsets one past this
          nextQuotePos = self.currentTokenStartOffset + self.currentLine[self.currentTokenStartOffset+1:].find("\"")
          self.currentToken = self.currentLine[self.currentTokenStartOffset:nextQuotePos+2]
          break
        elif s in Symbols(): # Symbol
          if s == "/" and endChar in ["/", "*"]: # comment not at start of line
            self.nextLine()
            tokenEndOffset = self.currentTokenStartOffset + 1
          else:
            self.currentToken = s
            break
        elif endChar == " " or endChar in Symbols():
          self.currentToken = s
          break
        else:
          tokenEndOffset += 1
      else:
        if endChar == " " or endChar in Symbols(): # Keyword or Identifier
          self.currentToken = s
          break
        else:
          tokenEndOffset += 1

  def skipCommentsEmptyLines(self):
    multiLineBlockComment = False
    #pdb.set_trace()
    while self.currentLine != None and (self.currentLine.startswith("//") or self.currentLine.startswith("/**") or self.currentLine in ["\n", "\r\n", "\t\n", "\t\r\n"] or len(self.currentLine.split()) == 0) or multiLineBlockComment: # Skip commentsa
      commentLineSplit = self.currentLine.split()
      if commentLineSplit:
        if commentLineSplit[0] == "/**" and not commentLineSplit[-1] == "*/":
          multiLineBlockComment = True
        elif multiLineBlockComment and commentLineSplit[-1] == "*/":
          multiLineBlockComment = False
      self.nextLine()

  def advance(self):
    self.skipCommentsEmptyLines()

    if not self.hasMoreTokens():
      return

    self.nextToken()

    tokenEndOffset = self.currentTokenStartOffset + len(self.currentToken)   
        
    if tokenEndOffset >= len(self.currentLine): # got to the end of the line? if so go back round to get first token of next line 
      self.nextLine()
      self.skipCommentsEmptyLines()
      if not self.hasMoreTokens():
        return
      self.nextToken()
      tokenEndOffset = self.currentTokenStartOffset + len(self.currentToken)   
    
    self.currentTokenStartOffset = tokenEndOffset

    print (self.currentLine)
    print (self.currentToken)
   
  def tokenType(self):
    if self.currentToken.upper() in Keywords():
      return TokenType.KEYWORD
    elif self.currentToken in Symbols():
      return TokenType.SYMBOL
    elif re.match("[a-zA-Z_]+[\w]*", self.currentToken):
      return TokenType.IDENTIFIER
    elif re.match('\d+', self.currentToken):
      return TokenType.INT_CONST
    elif re.match("\"[^\"\n]*\"", self.currentToken):
      return TokenType.STRING_CONST

  def symbol(self):
    if self.tokenType() == TokenType.SYMBOL:
      return self.currentToken

  def keyword(self):
    if self.tokenType() == TokenType.KEYWORD:
      return self.currentToken

  def identifier(self):
    if self.tokenType() == TokenType.IDENTIFIER:
      return self.currentToken

  def intVal(self):
    if self.tokenType() == TokenType.INT_CONST:
      return self.currentToken

  def stringVal(self):
    if self.tokenType() == TokenType.STRING_CONST:
      return self.currentToken[1:-1] # strip quotes
