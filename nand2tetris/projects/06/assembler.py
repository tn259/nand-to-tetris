import code
import command_types
import parser
import symbol_table
import sys
import os
import pdb


def main(filename):

  outputFilename = os.path.splitext(filename)[0]+".hack"
  st = symbol_table.SymbolTable()  

  # First pass store all LABELS
  p = parser.Parser(filename)
  p.advance()
  instructionCount = 0
  while p.hasMoreCommands():
    commandType = p.commandType()
    if p.commandType() == command_types.L_COMMAND: 
      symbol = p.symbol()
      st.addEntry(symbol, instructionCount)
    else:
      instructionCount += 1
    p.advance()

  # Second pass
  n = 16  
  p = parser.Parser(filename)
  p.advance()
  while p.hasMoreCommands():

    command = ""

    if p.commandType() == command_types.A_COMMAND:
      symbol = p.symbol()
      address = ""
      if st.contains(symbol):
        address = st.getAddress(symbol)
      elif symbol.isdigit():
        address = symbol
      else:
        st.addEntry(symbol, n)
        address = n
        n += 1
      command = format(int(address), '#018b')[2:]
    elif p.commandType() == command_types.C_COMMAND:
      command = "111" + code.comp(p.comp()) + code.dest(p.dest()) + code.jump(p.jump())

    if bool(command):
      with open(outputFilename, 'a') as outFile:
        outFile.write(command+"\n")

    p.advance()


if __name__ == "__main__":
  main(sys.argv[1])
