import Tokenizer
import glob
import sys
import os
import pdb

def main(arg):
  if arg.endswith(".jack"):
    jackFile = arg
    analyze(jackFile)
  else:
    directory = arg
    jackFiles = glob.glob(directory + "/*.jack")
    for f in jackFiles:
      analyze(f)

def charXMLify(char):
  if char == "<":
    return "&lt;"
  elif char == ">":
    return "&gt;"
  elif char == "&":
    return "&amp;"
  else:
    return char    
    
def analyze(jackFile):
  tokenizedXmlFilename = os.path.splitext(jackFile)[0]+"T.xml.cmp"
  outputFile = open(tokenizedXmlFilename, 'w')
  outputFile.write("<tokens>\r\n")
  t = Tokenizer.Tokenizer(jackFile)
  t.advance()
  while t.hasMoreTokens():
    tokenType = t.tokenType()
    if tokenType == Tokenizer.TokenType.KEYWORD:
      outputFile.write("<keyword> "+t.keyword()+" </keyword>")  
    elif tokenType == Tokenizer.TokenType.SYMBOL:
      outputFile.write("<symbol> "+charXMLify(t.symbol())+" </symbol>")  
    elif tokenType == Tokenizer.TokenType.IDENTIFIER:
      outputFile.write("<identifier> "+t.identifier()+" </identifier>")
    elif tokenType == Tokenizer.TokenType.INT_CONST:
      outputFile.write("<integerConstant> "+t.intVal()+" </integerConstant>")  
    elif tokenType == Tokenizer.TokenType.STRING_CONST:
      outputFile.write("<stringConstant> "+t.stringVal()+" </stringConstant>")
    else:
      pdb.set_trace()
      print("Invalid")
    outputFile.write("\r\n")
    t.advance()
  outputFile.write("</tokens>")
  outputFile.write("\r\n")
  outputFile.close()

if __name__ == "__main__":
  main(sys.argv[1])
