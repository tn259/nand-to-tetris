// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(START)
  @setting // reset var to 0
  M=0

  @KBD // get Keyboard input
  D=M

  @RESET_I // Go to setting loop if no input i.e. setting white
  D; JEQ

  @setting // otherwise setting is black
  M=-1

(RESET_I)
  @i
  M=0

(SET_LOOP)
  // Go back to start if i == 8192
  @i
  D=M
  @8192
  D=D-A
  @START
  D; JEQ 

  @setting // 0 or -1 ?
  D=M
  @CLEAR
  D; JEQ

  // 32 * 256 = 8192 iterations to set RAM[SCREEN+i] = -1
  @SCREEN // set RAM[SCREEN+i] to setting
  D=A
  @i
  A=D+M
  M=-1

  @ITERATE // skip clear section
  0; JMP

(CLEAR)
  // 32 * 256 = 8192 iterations to set RAM[SCREEN+i] = 0
  @SCREEN // set RAM[SCREEN+i] to setting
  D=A
  @i
  A=D+M
  M=0

(ITERATE)  
  @i
  M=M+1

  @SET_LOOP
  0; JMP
