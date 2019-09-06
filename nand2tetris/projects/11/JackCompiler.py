import Tokenizer
import CompilationEngine
import VMWriter
import glob
import sys
import os
import pdb

def main(arg):
  if arg.endswith(".jack"):
    jackFile = arg
    compileJack(jackFile)
  else:
    directory = arg
    jackFiles = glob.glob(directory + "/*.jack")
    for f in jackFiles:
      compileJack(f)


def compileJack(jackFile):
  outputFilename = os.path.splitext(jackFile)[0]+".vm"
  t = Tokenizer.Tokenizer(jackFile)
  vmw = VMWriter.VMWriter(outputFilename)
  ce = CompilationEngine.CompilationEngine(t, vmw)

  t.advance()
  if t.keyword() != "class":
    print("jack file does not have a class!")
    exit(1)

  ce.CompileClass()
  vmw.close()
   
if __name__ == "__main__":
    main(sys.argv[1])
