import command_types
import os
import pdb
from os import system

class CodeWriter:
  def __init__(self, filename):
    self.outputFilename = filename
    self.asm_file = open(filename, 'w')
    self.segmentTable = {
      "local": 1,
      "argument": 2,
      "this": 3,
      "that": 4,
      "temp": 5
    }
    self.binaryArithmeticCommands = [
      "add",
      "sub",
      "and",
      "or",
      "eq",
      "lt",
      "gt"
    ]
    self.eqCount = 1
    self.ltCount = 1
    self.gtCount = 1

  def WritePushPop(self, command, segment, index):
    ### Segment set 1
    # 0 SP
    # 1 LCL
    # 2 ARG
    # 3 THIS
    # 4 THAT
    ## PUSH: addr = segment + index, *SP = *addr, SP++
    ## POP: addr = segment + index, SP--, *addr=*SP

    ### Segment set 2
    # constant
    ## PUSH: *SP = i, SP++

    ### Segment set 3
    # static
    ## @<Filename>.index

    ### Segment set 4
    # 5 temp
    ## PUSH: addr = 5 + index, *SP = *addr, SP++
    ## POP: addr = 5 + index, SP--, *addr=*SP

    ### Segment set 5
    # pointer
    ## push pointer 0/1 -> PUSH: *SP = THIS/THAT, SP++
    ## pop pointer 0/1 -> POP: SP--, THIS/THAT = *SP

    addr = ''  

    # calculate addr based on segment
    if segment == "local" or segment == "argument" or segment == "this" or segment == "that":
      addr = str(self.segmentTable[segment])
    elif segment == "temp":
      #pdb.set_trace()
      addrNum = self.segmentTable[segment] + index
      addr = str(addrNum)
    elif segment == "constant":
      if command == command_types.C_POP:
        # invalid
        return None
      addr = str(index)
    elif segment == "pointer":
      if index == 0:
        addr = str(self.segmentTable["this"])
      elif index == 1:
        addr = str(self.segmentTable["that"])
      else:
        # invalid
        return None
    elif segment == "static":
      # addr = str(<filename without ext>.index)
      staticName = os.path.splitext(os.path.basename(self.outputFilename))[0]
      addr = staticName + "." + str(index)
    else:
      # invalid
      return None

    if command == command_types.C_PUSH:
      self.writeASMCommandToFile("// push "+segment+" "+str(index)) # D=addr

      if segment == "temp" or segment == "constant" or segment == "static" or segment == "pointer":
        self.writeASMCommandToFile("@"+addr)
      else:
        self.writeASMCommandToFile("@"+str(index))
        self.writeASMCommandToFile("D=A") # save bas address in d
        self.writeASMCommandToFile("@"+addr)
        self.writeASMCommandToFile("A=M+D") # address index offset and save into d

      if segment == "constant":
        self.writeASMCommandToFile("D=A")
      else:
        self.writeASMCommandToFile("D=M")

      self.writeASMCommandToFile("@SP") # *SP=D
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("M=D")
      self.writeASMCommandToFile("@SP") # SP++
      self.writeASMCommandToFile("M=M+1")
    elif command == command_types.C_POP:
      self.writeASMCommandToFile("// pop "+segment+" "+str(index)) # D=addr
      self.writeASMCommandToFile("@SP") # SP--
      self.writeASMCommandToFile("M=M-1")
      self.writeASMCommandToFile("@SP") # D=*SP
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("D=M")
      

      if segment == "temp" or segment == "static" or segment == "pointer":
        self.writeASMCommandToFile("@"+addr)
        self.writeASMCommandToFile("M=D")
      else:
        self.writeASMCommandToFile("@5") # save D to temp 
        self.writeASMCommandToFile("M=D")
        self.writeASMCommandToFile("@"+str(index))
        self.writeASMCommandToFile("D=A") # save base address in D
        self.writeASMCommandToFile("@"+addr)
        self.writeASMCommandToFile("A=M+D") # address base + index
        self.writeASMCommandToFile("D=A") # save final address
        self.writeASMCommandToFile("@6") # save D to temp 
        self.writeASMCommandToFile("M=D")
        self.writeASMCommandToFile("@5") # get origianl SP value back out
        self.writeASMCommandToFile("D=M")
        self.writeASMCommandToFile("@6") # go back to final address
        self.writeASMCommandToFile("A=M")
        self.writeASMCommandToFile("M=D") # save SP value in final address


  def WriteArithmetic(self, command):
    self.writeASMCommandToFile("// "+command)

    if command in self.binaryArithmeticCommands:

      #       |x|
      #       |y|
      # SP -> | |
      self.WritePushPop(command_types.C_POP, "temp", 0) # write y onto temp

      #       |x|
      # SP -> | |
      self.writeASMCommandToFile("@SP") # SP--
      self.writeASMCommandToFile("M=M-1")

      # SP -> |x|
      self.writeASMCommandToFile("@5")
      self.writeASMCommandToFile("D=M") # D=y
      self.writeASMCommandToFile("@SP")
      self.writeASMCommandToFile("A=M")

      # Write result to position of x (M is x, D is y)
      if command == "add":
        self.writeASMCommandToFile("M=D+M")
      elif command == "sub":
        self.writeASMCommandToFile("M=M-D")
      elif command == "and":
        self.writeASMCommandToFile("M=D&M")
      elif command == "or":
        self.writeASMCommandToFile("M=D|M")
      elif command == "eq":
        self.writeEqLtGtStatements("eq", self.eqCount)
        self.eqCount += 1
      elif command == "lt":
        self.writeEqLtGtStatements("lt", self.ltCount)
        self.ltCount += 1
      elif command == "gt":
        self.writeEqLtGtStatements("gt", self.gtCount)
        self.gtCount += 1
      else:
        # invalid
        pass

      # put SP back
      self.writeASMCommandToFile("@SP") # SP++
      self.writeASMCommandToFile("M=M+1")
    elif command == "neg":
      #       |x|
      # SP -> | |
      self.writeASMCommandToFile("@SP") # SP--
      self.writeASMCommandToFile("M=M-1")
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("M=-M")
      # put SP back
      self.writeASMCommandToFile("@SP") # SP++
      self.writeASMCommandToFile("M=M+1")
    elif command == "not":
      #       |x|
      # SP -> | |
      self.writeASMCommandToFile("@SP") # SP--
      self.writeASMCommandToFile("M=M-1")
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("M=!M")
      # put SP back
      self.writeASMCommandToFile("@SP") # SP++
      self.writeASMCommandToFile("M=M+1")
    else:
      return None
       

  def writeEqLtGtStatements(self, comparison, count):
    countStr = str(count)
    comparisonUpper = comparison.upper()
    self.writeASMCommandToFile("D=M-D")
    self.writeASMCommandToFile("@"+comparisonUpper+"_"+countStr)
    self.writeASMCommandToFile("D;J"+comparisonUpper)
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("M=0")
    self.writeASMCommandToFile("@CONT_"+comparisonUpper+"_"+countStr)
    self.writeASMCommandToFile("0;JMP")
    self.writeASMCommandToFile("("+comparisonUpper+"_"+countStr+")")
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("M=-1")
    self.writeASMCommandToFile("(CONT_"+comparisonUpper+"_"+countStr+")")
    

  def writeASMCommandToFile(self, command):
    self.asm_file.write(command+"\n")

  def Close(self):
    self.asm_file.close()
