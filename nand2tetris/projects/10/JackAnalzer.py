import Tokenizer
import CompilationEngine
import glob
import sys
import os
import pdb

def main(arg, tokenizeOnly=False):
  if arg.endswith(".jack"):
    jackFile = arg
    if tokenizeOnly:
      analyzeT(jackFile)
    else:
      analyze(jackFile)
  else:
    directory = arg
    jackFiles = glob.glob(directory + "/*.jack")
    for f in jackFiles:
      if tokenizeOnly:
        analyzeT(f)
      else:
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
  outputFilename = os.path.splitext(jackFile)[0]+".xml.cmp"
  t = Tokenizer.Tokenizer(jackFile)
  ce = CompilationEngine.CompilationEngine(t, outputFilename)

  t.advance()
  if t.keyword() != "class":
    print("jack file does not have a class!")
    exit(1)

  ce.CompileClass()
   
    
def analyzeT(jackFile):
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
  if len(sys.argv) == 3 and argv[2] == "--tokenize_only": 
    main(sys.argv[1], True)
  else:
    main(sys.argv[1])
