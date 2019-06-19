import command_types
import os
import pdb

class CodeWriter:
  def __init__(self, filename):
    self.outputFilename = filename
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
    self.filenamePrefix = os.path.splitext(os.path.basename(self.outputFilename))[0]
    self.currentFunction = ""
    self.callCount = 1

  def completeLabel(self, functionName, label):
    completeLabel = self.filenamePrefix+"."+functionName
    if label:
      completeLabel += "$"+label
    return completeLabel

  def WriteInit(self):
    self.writeASMCommandToFile("// Bootstrap") # SP points to 256
    self.writeASMCommandToFile("@256")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("M=D")
    self.WriteCall("Sys.init", 0) # call Sys.init

  def WriteLabel(self, label):
    self.writeASMCommandToFile("// label "+str(label))
    self.writeASMCommandToFile("("+self.completeLabel(self.currentFunction, label)+")")
    
  def WriteGoto(self, label, functionName=""):
    if not functionName:
      functionName = self.currentFunction
    self.writeASMCommandToFile("// goto "+str(label))
    self.writeASMCommandToFile("@"+self.completeLabel(functionName, label))
    self.writeASMCommandToFile("0;JMP")

  def WriteIf(self, label):
    self.writeASMCommandToFile("// if-goto "+str(label))
    self.WritePushPop(command_types.C_POP, "temp", 0) # write cond onto temp
    self.writeASMCommandToFile("@"+str(self.segmentTable["temp"]))
    self.writeASMCommandToFile("D=M") # save cond into D
    self.writeASMCommandToFile("@"+self.completeLabel(self.currentFunction, label))
    self.writeASMCommandToFile("D;JNE") # if true i.e. if not false
    
  def WriteFunction(self, functionName, numVars):
    self.writeASMCommandToFile("// function "+str(functionName)+" "+str(numVars))

    self.currentFunction = functionName
    self.writeASMCommandToFile("("+self.completeLabel(self.currentFunction, "")+")")
    for i in range(numVars):
      self.WritePushPop(command_types.C_PUSH, "constant", 0)

  def WriteCall(self, functionName, numArgs):
    self.writeASMCommandToFile("// call "+str(functionName)+" "+str(numArgs))

    returnLabel = "RET."+str(self.callCount)
    self.WritePushPop(command_types.C_PUSH, self.completeLabel(self.currentFunction, returnLabel), 0)
    self.WritePushPop(command_types.C_PUSH, "local", 0)
    self.WritePushPop(command_types.C_PUSH, "argument", 0)
    self.WritePushPop(command_types.C_PUSH, "this", 0)
    self.WritePushPop(command_types.C_PUSH, "that", 0)
    
    # ARG=SP-5-nArgs
    self.writeASMCommandToFile("@SP") # Save SP to temp
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["temp"]))
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@5") # Save 5 to D
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["temp"])) # SP - 5
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("@"+str(numArgs)) # Save numArgs to D
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["temp"])) # (SP - 5) - numArgs
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["argument"])) # ARG = (SP - 5) - numArgs
    self.writeASMCommandToFile("M=D")

    # LCL = SP
    self.writeASMCommandToFile("@SP") # Save SP to D
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["local"]))
    self.writeASMCommandToFile("M=D")

    self.WriteGoto("", functionName)
    self.WriteLabel(returnLabel)

    self.callCount += 1
    

  def WriteReturn(self):
    self.writeASMCommandToFile("// return")

    endFrame = "R13"
    retAddr = "R14"

    # endFrame = LCL
    self.writeASMCommandToFile("@"+str(self.segmentTable["local"]))
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("M=D")

    # retAddr = *(endFrame - 5) 
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+retAddr)
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@5")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+retAddr)
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+retAddr)
    self.writeASMCommandToFile("M=D")

    # *ARG = pop()
    self.WritePushPop(command_types.C_POP, "argument", 0)
    
    # SP = ARG+1
    self.writeASMCommandToFile("@"+str(self.segmentTable["argument"]))
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@1")
    self.writeASMCommandToFile("D=D+A")
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("M=D")

    # THAT = *(endFrame-1)
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["that"]))
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@1")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["that"]))
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["that"]))
    self.writeASMCommandToFile("M=D")
    
    # THIS = *(endFrame-2)
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["this"]))
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@2")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["this"]))
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["this"]))
    self.writeASMCommandToFile("M=D")

    # ARG = *(endFrame-3)
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["argument"]))
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@3")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["argument"]))
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["argument"]))
    self.writeASMCommandToFile("M=D")

    # LCL = *(endFrame-4)
    self.writeASMCommandToFile("@"+endFrame)
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["local"]))
    self.writeASMCommandToFile("M=D")
    self.writeASMCommandToFile("@4")
    self.writeASMCommandToFile("D=A")
    self.writeASMCommandToFile("@"+str(self.segmentTable["local"]))
    self.writeASMCommandToFile("M=M-D")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("D=M")
    self.writeASMCommandToFile("@"+str(self.segmentTable["local"]))
    self.writeASMCommandToFile("M=D")

    # goto retAddr
    self.writeASMCommandToFile("@"+retAddr)
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("0;JMP")

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
      addr = self.filenamePrefix + "." + str(index)
    elif "RET" in segment:
      addr = segment
    else:
      # invalid
      return None

    if command == command_types.C_PUSH:
      self.writeASMCommandToFile("// push "+segment+" "+str(index)) # D=addr

      if segment == "temp" or segment == "constant" or segment == "static" or segment == "pointer" or "RET" in segment:
        self.writeASMCommandToFile("@"+addr)
      else:
        self.writeASMCommandToFile("@"+str(index))
        self.writeASMCommandToFile("D=A") # save bas address in d
        self.writeASMCommandToFile("@"+addr)
        self.writeASMCommandToFile("A=M+D") # address index offset and save into d

      if segment == "constant" or "RET" in segment:
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
        self.writeASMCommandToFile("@"+str(self.segmentTable["temp"])) # save D to temp 
        self.writeASMCommandToFile("M=D")
        self.writeASMCommandToFile("@"+str(index))
        self.writeASMCommandToFile("D=A") # save base address in D
        self.writeASMCommandToFile("@"+addr)
        self.writeASMCommandToFile("A=M+D") # address base + index
        self.writeASMCommandToFile("D=A") # save final address
        self.writeASMCommandToFile("@"+str(self.segmentTable["temp"]+1)) # save D to temp 
        self.writeASMCommandToFile("M=D")
        self.writeASMCommandToFile("@"+str(self.segmentTable["temp"])) # get origianl SP value back out
        self.writeASMCommandToFile("D=M")
        self.writeASMCommandToFile("@"+str(self.segmentTable["temp"]+1)) # go back to final address
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
      self.writeASMCommandToFile("@"+str(self.segmentTable["temp"]))
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
    self.writeASMCommandToFile("@"+self.completeLabel(self.currentFunction, comparisonUpper+"_"+countStr))
    self.writeASMCommandToFile("D;J"+comparisonUpper)
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("M=0")
    self.writeASMCommandToFile("@"+self.completeLabel(self.currentFunction, "CONT_"+comparisonUpper+"_"+countStr))
    self.writeASMCommandToFile("0;JMP")
    self.writeASMCommandToFile("("+self.completeLabel(self.currentFunction, comparisonUpper+"_"+countStr)+")")
    self.writeASMCommandToFile("@SP")
    self.writeASMCommandToFile("A=M")
    self.writeASMCommandToFile("M=-1")
    self.writeASMCommandToFile("("+self.completeLabel(self.currentFunction, "CONT_"+comparisonUpper+"_"+countStr)+")")
    

  def writeASMCommandToFile(self, command):
    with open(self.outputFilename, 'a') as outFile:
      outFile.write(command+"\n")
