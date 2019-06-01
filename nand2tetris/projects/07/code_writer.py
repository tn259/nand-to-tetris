import command_types
import os

class CodeWriter:
  def __init__(self, filename):
    self.outputFilename = filename
    self.segmentTable = {
      "local": 1,
      "arg": 2,
      "this": 3,
      "that": 4,
      "temp": 5
    }

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
    if segment == "local" or segment == "arg" or segment == "this" or segment == "that" or segment == "temp":
      addr = str(self.segmentTable[segment] + index)
    elif segment == "constant":
      if command == command_types.C_POP:
        # invalid
      addr = str(index)
    elif segment == "pointer":
      if index == 0:
        addr = str(self.segmentTable["this"])
      elif index == 1:
        addr = str(self.segmentTable["that"])
      else:
        # invalid
    elif segment == "static":
      # addr = str(<filename without ext>.index)
      staticName = os.path.splitext(os.path.basename(self.outputFilename))[0]
      addr = staticName + "." + str(index)
    else:
      # invalid

    if command == command_types.C_PUSH:
      self.writeASMCommandToFile("@"+addr) # D=addr
      self.writeASMCommandToFile("D=A")
      self.writeASMCommandToFile("@SP") # *SP=D
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("M=D")
      self.writeASMCommandToFile("@SP") # SP++
      self.writeASMCommandToFile("M=M+1")
    elif command == command_types.C_POP:
      self.writeASMCommandToFile("@SP") # SP--
      self.writeASMCommandToFile("M=M-1")
      self.writeASMCommandToFile("@SP") # D=SP
      self.writeASMCommandToFile("D=A")
      self.writeASMCommandToFile("@"+addr) # *addr=D
      self.writeASMCommandToFile("A=M")
      self.writeASMCommandToFile("M=D")
      

  def writeASMCommandToFile(self, command):
    with open(self.outputFilename, 'a') as outFile:
      outFile.write(command+"\n")
