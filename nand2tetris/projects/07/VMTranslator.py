import code_writer
import command_types
import parser
import sys
import os
import pdb
from os import system

class VMTranslator:

  def run(self, filename):

    print("Filename: "+str(filename))

    # Second pass
    outputFilename = os.path.splitext(filename)[0]+".asm"
    print("outputFilename: "+str(outputFilename))

    p = parser.Parser(filename)
    cw = code_writer.CodeWriter(outputFilename)

    print("Start advance")

    p.advance()
    while p.hasMoreCommands():

      commandType = p.commandType()

      if commandType == command_types.C_PUSH or commandType == command_types.C_POP:
        cw.WritePushPop(commandType, p.arg1(), p.arg2())
      elif commandType == command_types.C_ARITHMETIC:
        cw.WriteArithmetic(p.arg1())
      else:
        # Unimplemented
        pass

      p.advance()

    print("Finished") 
    cw.Close()

if __name__ == "__main__":
  vm = VMTranslator()
  vm.run(sys.argv[1])
