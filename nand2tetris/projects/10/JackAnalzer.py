import Tokenizer
import glob
import sys
import os
import pdb

def main(arg):
  if arg.endswith(".jack"):
    jackFile = arg
    tokenize(jackFile)
  else:
    directory = arg
    jackFiles = glob.glob(directory + "/*.jack")
    for f in jackFiles:
      tokenize(f)
    
    
def tokenize(jackFile):
  tokenizedTextFilename = os.path.splitext(jackFile)[0]+".txt"
  outputFile = open(tokenizedTextFilename, 'w')
  t = Tokenizer.Tokenizer(jackFile)
  while t.hasMoreTokens():
    t.advance()
    pdb.set_trace()
    tokenType = t.tokenType()
    if tokenType == Tokenizer.TokenType.KEYWORD:
      outputFile.write(t.keyword())  
    elif tokenType == Tokenizer.TokenType.SYMBOL:
      outputFile.write(t.symbol())  
    elif tokenType == Tokenizer.TokenType.IDENTIFIER:
      outputFile.write(t.identifier())
    elif tokenType == Tokenizer.TokenType.INT_CONST:
      outputFile.write(t.intVal())  
    elif tokenType == Tokenizer.TokenType.STRING_CONST:
      outputFile.write(t.stringVal())
    outputFile.write("\n")
  outputFile.close()

if __name__ == "__main__":
  main(sys.argv[1])
