// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

// Set RAM[2]=0
  @0
  D=A
  @R2
  M=D

// Set RAM[iterations]=RAM[1]
  @R1
  D=M
  @iterations
  M=D

// got end if RAM[iterations]==0
  @END
  D; JEQ

// Start of loop
(LOOP)

// Add R[0] to R[2]
  @R0
  D=M
  @R2
  M=M+D

// Decrease iter
  @iterations
  M=M-1

// Go to end if R[iterations] is now 0
  D=M
  @END
  D; JLE

// Back to top of loop
  @LOOP
  0; JMP

(END)
  @END
  0; JMP
