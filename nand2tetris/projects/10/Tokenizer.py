from enum import Enum
import re

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

  def advance(self):
    if not self.hasMoreTokens():
      print("Tokenizer::advance has reached the end")
      return

    while self.currentLine.startswith("//") or self.currentLine.startswith("/**"): # Skip comments
      self.nextLine()

    # Process Line
    tokenEndOffset = self.currentTokenStartOffset + 1
    while tokenEndOffset < len(self.currentLine):
      s = self.currentLine[self.currentTokenStartOffset:tokenEndOffset]
      endChar = self.currentLine[tokenEndOffset]
      if len(s) == 1:
        if s in ["\t", "\r", " "]: # Skip over tabs, CR and spaces
          self.currentTokenStartOffset += 1
          tokenEndOffset += 1
        elif s == "\"": # string const find closing " and return update offsets one past this
          nextQuotePos = self.currentLine[self.currentTokenStartOffset+1:].find("\"")
          self.currentToken = self.currentLine[self.currentTokenStartOffset:nextQuotePos+1]
          break
        elif s in Symbols(): # Symbol
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
            
    if tokenEndOffset >= len(self.currentLine): # got to the end of the line?
      self.nextLine()
    else:
      self.currentTokenStartOffset = tokenEndOffset
        
    
  def tokenType(self):
    if self.currentToken.upper() in Keywords():
      return KEYWORD
    elif self.currentToken in Symbols():
      return SYMBOL
    elif re.match("[a-zA-Z_][\w]+", self.currentToken):
      return IDENTIFIER
    elif re.match('\d+', self.currentToken):
      return INT_CONST
    elif re.match("\"[^\"\n]*\"", self.currentToken):
      return STRING_CONST

  def symbol(self):
    if self.tokenType() == SYMBOL:
      return self.currentToken

  def keyword(self):
    if self.tokenType() == KEYWORD:
      return self.currentToken

  def identifier(self):
    if self.tokenType() == IDENTIFIER:
      return self.currentToken

  def intVal(self):
    if self.tokenType() == INT_CONST:
      return self.currentToken

  def stringVal(self):
    if self.tokenType() == STRING_CONST:
      return self.currentToken[1:-1] # strip quotes
