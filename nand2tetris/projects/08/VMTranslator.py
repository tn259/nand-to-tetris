import code_writer
import command_types
import parser
import sys
import os
import pdb
import glob

def main(arg):

  if arg.endswith(".vm"):
    vmFilename = arg
    asmFilename = os.path.splitext(vmFilename)[0]+".asm"
    vm = VMTranslator()
    vm.run(vmFilename, asmFilename)
  else:
    # Directory of .vm files
    directory = arg
    vmFilenames = glob.glob(directory + "/*.vm")
    asmFilename = directory + "/" + directory[directory.rfind('/')+1:] + ".asm"
    for vmFilename in vmFilenames:
      print vmFilename
      vm = VMTranslator()
      vm.run(vmFilename, asmFilename)

class VMTranslator:

  def run(self, vmFilename, asmFilename):

    p = parser.Parser(vmFilename)
    cw = code_writer.CodeWriter(asmFilename)

    p.advance()
    while p.hasMoreCommands():

      commandType = p.commandType()

      if commandType == command_types.C_PUSH or commandType == command_types.C_POP:
        cw.WritePushPop(commandType, p.arg1(), p.arg2())
      elif commandType == command_types.C_ARITHMETIC:
        cw.WriteArithmetic(p.arg1())
      elif commandType == command_types.C_LABEL:
        cw.WriteLabel(p.arg1())
      elif commandType == command_types.C_GOTO:
        cw.WriteGoto(p.arg1())
      elif commandType == command_types.C_IF:
        cw.WriteIf(p.arg1())
      elif commandType == command_types.C_FUNCTION:
        cw.WriteFunction(p.arg1(), p.arg2())
      elif commandType == command_types.C_RETURN:
        cw.WriteReturn()
      elif commandType == command_types.C_CALL:
        cw.WriteCall(p.arg1(), p.arg2())
      else:
        # Unimplemented
        pass

      p.advance()


if __name__ == "__main__":
  main(sys.argv[1])
