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
    vm = VMTranslator(asmFilename)
    vm.run(vmFilename)
  else:
    # Directory of .vm files
    directory = arg
    vmFilenames = glob.glob(directory + "/*.vm")
    asmFilename = directory + "/" + directory[directory.rfind('/')+1:] + ".asm"
    vm = VMTranslator(asmFilename, True)
    for vmFilename in vmFilenames:
      vm.run(vmFilename)

class VMTranslator:

  def __init__(self, asmFilename, writeInit=False):
    self.cw = code_writer.CodeWriter(asmFilename)
    if writeInit:
      self.cw.WriteInit()
    

  def run(self, vmFilename):

    p = parser.Parser(vmFilename)
    self.cw.setStaticPrefix(vmFilename)

    p.advance()
    while p.hasMoreCommands():

      commandType = p.commandType()

      if commandType == command_types.C_PUSH or commandType == command_types.C_POP:
        self.cw.WritePushPop(commandType, p.arg1(), p.arg2())
      elif commandType == command_types.C_ARITHMETIC:
        self.cw.WriteArithmetic(p.arg1())
      elif commandType == command_types.C_LABEL:
        self.cw.WriteLabel(p.arg1())
      elif commandType == command_types.C_GOTO:
        self.cw.WriteGoto(p.arg1())
      elif commandType == command_types.C_IF:
        self.cw.WriteIf(p.arg1())
      elif commandType == command_types.C_FUNCTION:
        self.cw.WriteFunction(p.arg1(), p.arg2())
      elif commandType == command_types.C_RETURN:
        self.cw.WriteReturn()
      elif commandType == command_types.C_CALL:
        self.cw.WriteCall(p.arg1(), p.arg2())
      else:
        # Unimplemented
        pass

      p.advance()


if __name__ == "__main__":
  main(sys.argv[1])
