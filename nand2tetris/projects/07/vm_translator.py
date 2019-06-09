import code_writer
import command_types
import parser
import sys
import os
import pdb


def main(filename):

  # Second pass
  outputFilename = os.path.splitext(filename)[0]+".asm"

  p = parser.Parser(filename)
  cw = code_writer.CodeWriter(outputFilename)

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


if __name__ == "__main__":
  main(sys.argv[1])
