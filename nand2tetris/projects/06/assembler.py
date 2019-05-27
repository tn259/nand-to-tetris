import code
import command_types
import parser
import sys
import os
import pdb


def main(filename):
  pdb.set_trace()
  outputFilename = os.path.splitext(filename)[0]+".hack"
  
  p = parser.Parser(filename)
  p.advance()
  while p.hasMoreCommands():

    command = ""

    if p.commandType() == command_types.A_COMMAND:
      symbol = p.symbol()
      command = format(int(symbol), '#018b')[2:]
    elif p.commandType() == command_types.C_COMMAND:
      command = "111" + code.comp(p.comp()) + code.dest(p.dest()) + code.jump(p.jump())

    if bool(command):
      with open(outputFilename, 'a') as outFile:
        outFile.write(command+"\r\n")

    p.advance()


if __name__ == "__main__":
  main(sys.argv[1])
