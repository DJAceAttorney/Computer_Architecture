#   File:       Project.py
#   Author:     Fardeen Yaqub 
#   Date:       12/6/2020
#   E-mail:     fyaqub1@umbc.edu 
#   Class:      UMBC CMSC 411 - Computer Architecture (FA 2020)
                

#GLOBAL VARIABLES
#used for storing MIP instructions
instructions = []

#FLOAT POINT REGISTERS
fpReg = [float(0)] * 32

#INTEGER POINT REGISTERS
intReg = [0] * 32

#MEMORY VALUES
value_Memory = [45,12,0,0,10,135,254,127,18,4,55,8,2,98,13,5,233,158,167]
length_memory = len(value_Memory)

#INSTRUCTIONS
LOAD_INST = "L.D"
STORE_INST = "S.D"
ADD_INST = "ADD"
MULD_INST = "MUL.D"
SUBD_INST = "SUB.D"
DIVD_INST = "DIV.D"
ADDI_INST = "ADDI"
ADDD_INST = "ADD.D"
SUB_INST = "SUB"

#Register position in instruction
DEST_REG = 1
SOURCE_ONE = 2
SOURCE_TWO = 3

#Latencies
INT_LATENCY = 1
ADD_LATENCY = 2
MUL_LATENCY = 10
DIV_LATENCY = 40

STALL = "stall"
EMPTY_SPACE = " "

#hazard stall constants
WAW_STALL = "WAW_STALL"
WAR_STALL = "WAR_STALL"
RAW_STALL = "RAW_STALL"

pipeline_hazard = "pipeline_hazard"

#stalls at issue due to Busy Pipeline
stall_issue= -1

#stalls at issue for hazards
stall_issueAtWAW = -1
stall_issueAtWAR = -1
stall_issueAtRAW = -1

#stalls at read
stall_read = -1

#stalls at WB
stall_WB = 0

#currently stalling
is_stalling = False

#keeps track of each instruction that is completed --> we know that the FU is not a hazard
Row_not_full = 0
stalling_due_to_WAW = False
stalling_due_to_WAR = False
stalling_due_to_RAW = False
clock_cycle = 0

instr_len = 8

#checks if the board is filled up
def boardFull():
    for i in range(len(instructions)):
       if instructions[i][7] == EMPTY_SPACE or instructions[i][7] == STALL:
          return False

    #board is full        
    return True

#Here are all the hazard checks
#waw takes in the current row index and a string instruction
def waw(row_index, instruction):

    for i in range(row_index-1, Row_not_full-1, -1):

        #can't have a read after write if we're in the S.D state && checking the previous row utilizing the destination register
        if (instruction != STORE_INST) and (instructions[i][DEST_REG] == instructions[row_index][DEST_REG]):
            return True

    return False

#raw takes in the current row index and a string instruction
def raw(row_index, instruction):
    for i in range(row_index-1, Row_not_full-1, -1):

        #previous destination register is the same as the current register we want to write to
        if instruction == STORE_INST: 
            if instructions[i][DEST_REG] == instructions[row_index][DEST_REG]:
                return True

        #instruction destination register --> it is checking if the current instruction is utilizing the "previous register"
        elif instructions[i][DEST_REG] == instructions[row_index][SOURCE_ONE]:
            return True

        elif instructions[i][DEST_REG] == instructions[row_index][SOURCE_TWO]:
            return True
            
    #No Hazards
    return False

#war takes in current row index and a string instruction 
def war(row_index, instruction):
    for i in range(row_index - 1, Row_not_full - 1, -1):

        #can't have war when instruction is at S.D
        if instruction != STORE_INST and ((instructions[i][SOURCE_ONE] == instructions[row_index][DEST_REG]) or (instructions[i][SOURCE_TWO] == instructions[row_index][DEST_REG])):
            return True
    #No WAR hazard
    return False

#prints the table
def printBoard():

    print("Instruction", end="")
    print("\t", "\t", "ISSUE", "\t", "READ", "\t", "EX", "\t", "WB")
    print("----------------------------------------------------")

    for i in range(len(instructions)):
            for j in range(len(instructions[i])):

                print(instructions[i][j] , EMPTY_SPACE, end="")

                if j >=3:
                    print("\t" , end="")

            print("\n")

    print("Integer Registers", "\t", "Floating Point Registers" )
    print("-----------------", "\t", "------------------------" )

    for i in range(32):
        print("$", i, " = ", intReg[i], "\t", "\t", "\t", "\t", "F", i, " = ", fpReg[i], sep='')

#takes the numbers from the text file and uses them as indeces to find the register or memory address
def compute_registers(instruction, row_index):

    #ALU INSTRUCTION = L.D (Loading)
    if instruction == LOAD_INST:

        #finds the position of the string value we're looking for
        target = instructions[row_index][DEST_REG]
        source = instructions[row_index][SOURCE_ONE]

        #finds the target index
        point1 = target.find("F") 
        target_index = int(target[point1+1: ])

        #finds how much the offset is going to be
        point3 = source.find(EMPTY_SPACE) 
        point4 = source.find("(") 
        off_set = int(source[point3 +1 : point4])


        #finds the memory address index
        point5 = source.find("(") 
        point6 = source.find(")")  
        memory_address = int(source[point5 + 1 :point6])

        #adds offset to memory address and takes that index and stores it into our target index
        array_value = memory_address + off_set

        if memory_address + off_set > length_memory:
            array_value = memory_address + off_set - length_memory


        fpReg[target_index] = float(value_Memory[array_value])

    #ALU INSTRUCTION = S.D (storing)
    elif instruction == STORE_INST:
        target = instructions[row_index][SOURCE_ONE]
        source = instructions[row_index][DEST_REG]

        #finds the offset
        point1 = target.find(EMPTY_SPACE) 
        point2 = target.find("(") 
        off_set = int(target[point1 + 1: point2])

        
        #finds the memory address
        point3 = target.find("(") 
        point4 = target.find(")")         
        memory_address = int(target[point3 +1 : point4])

        #finds the target index
        point5 = source.find("F")  
        target_index = int(source[point5+1:])

        #stores the targeted index at the memory address with the off set accounted for
        value_Memory[memory_address + off_set] = fpReg[target_index]

    #ALU INSTRUCTION = ADD
    elif instruction == ADD_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the target index
        point1 = target.find("$")  
        target_index = int(target[point1 + 1:  ])

        #finds the first source
        point3 = first_value.find("$") 
        first_value_index = int(first_value[point3 + 1: ])

        #finds the second source
        point5 = second_value.find("$")  
        second_value_index = int(second_value[point5 + 1: ])

        #Adds the first and second source and stores in target source
        intReg[target_index] = intReg[first_value_index] + intReg[second_value_index]

    #ALU INSTRUCTION = ADDI
    elif instruction == ADDI_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds our Destination Register
        point1 = target.find("$") 
        target_index = int(target[point1 + 1: ])

        #finds our first source
        point3 = first_value.find("$")   
        first_value_index = int(first_value[point3 +1 : ])

        #adds immediate to first source index 
        intReg[target_index] = intReg[first_value_index] + int(second_value)

    #ALU INSTRUCTION = ADD.D
    elif instruction == ADDD_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the destination register
        point1 = target.find("F") 
        target_index = int(target[point1 + 1: ])

        #finds the first source
        point2 = first_value.find("F") 
        first_value_index = int(first_value[point2 + 1: ])

        #finds the second source
        point3 = second_value.find("F")  
        second_value_index = int(second_value[point3 + 1: ])

        #Adds the first and second source and stores in destination register
        fpReg[target_index] = float(fpReg[first_value_index] + fpReg[second_value_index])

    #ALU INSTRUCTION = SUB
    elif instruction == SUB_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the Destination Register
        point1 = target.find("$") 
        
        target_index = int(target[point1 + 1: ])

        #finds the first source
        point3 = first_value.find("$") 
          
        first_value_index = int(first_value[point3 + 1: ])

        #finds the second source
        point5 = second_value.find("$") 
         
        second_value_index = int(second_value[point5 + 1: ])

        #Subtracts the first and second source and stores in destination register
        intReg[target_index] = intReg[first_value_index] - intReg[second_value_index]

    #ALU INSTRUCTION = SUB.D
    elif instruction == SUBD_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the Destination Register
        point1 = target.find("F") 
        target_index = int(target[point1 + 1:])

        #finds the first source
        point3 = first_value.find("F") 
        first_value_index = int(first_value[point3 + 1: ])

        #finds the second source
        point5 = second_value.find("F")  
        second_value_index = int(second_value[point5 + 1: ])

        #Subtracts the first and second source and stores in destination register
        fpReg[target_index] = float(fpReg[first_value_index] - fpReg[second_value_index])

    #ALU INSTRUCTION = MUL.D

    elif instruction == MULD_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the target index
        point1 = target.find("F") 
        target_index = int(target[point1 + 1: ])

        #finds the first source
        point2 = first_value.find("F")   
        first_value_index = int(first_value[point2 + 1:])

        #finds the second source
        point3 = second_value.find("F") 
        second_value_index = int(second_value[point3 + 1:])

        #Multiplies the first and second source and stores in destination register
        fpReg[target_index] = float(fpReg[first_value_index] * fpReg[second_value_index])

    #ALU INSTRUCTION = DIV.D
    elif instruction == DIVD_INST:
        target = instructions[row_index][DEST_REG]
        first_value = instructions[row_index][SOURCE_ONE]
        second_value = instructions[row_index][SOURCE_TWO]

        #finds the target index
        point1 = target.find("F") 
        target_index = int(target[point1 + 1: ])

        #finds the first source
        point3 = first_value.find("F") 
        first_value_index = int(first_value[point3 + 1: ])

        #finds the second source
        point5 = second_value.find("F") 
        second_value_index = int(second_value[point5 + 1: ])

        if fpReg[second_value_index] == 0:
           raise Exception("Cannot Divide by 0 ")

        #Divides the first and second source and stores in destination register
        fpReg[target_index] = float(fpReg[first_value_index] / fpReg[second_value_index])  

def loadFile():

    index = 0

    file = input("Enter your file name: ")

    #Runs while still reading the file
    with open(file, 'r') as file:
        for instruction in file:

            instructions.append(instruction.split())
            
            #fills in empty spaces
            while len(instructions[index]) < 8:
                instructions[index].append(EMPTY_SPACE)

            index+=1

        #strips out the , 
        for i in range(len(instructions)):
            for j in range(len(instructions[i])):
                instructions[i][j] = instructions[i][j].strip(",")


    print()
    
        
def updateBoard(current_row, current_index, is_busy):

    empty_index = 0

    count = 4

    #Global variables that we're gonna change
    global is_stalling
    global stall_issueAtWAW
    global stall_issueAtWAR
    global stalling_due_to_WAR
    global stall_issue
    global stall_WB
    global stall_read
    global stalling_due_to_WAW
    global instr_len 
    global Row_not_full
    global stall_issueAtRAW
    global stalling_due_to_RAW


    #finds the first empty index in the row
    for i in range (count, instr_len):
        if current_row[i] == EMPTY_SPACE or current_row[i] == STALL:
            empty_index = i
            break

    #empty index is the issue stage
    if empty_index == 4:
        
        instruction = instructions[current_index][0]
    
        #returns a bool --> indicating if pipline is busy
        pipeline_busy = pipelineBusy(current_row, current_index)

        #check if stalling at issue stage
        if (instructions[current_index][4] == STALL and instructions[stall_issue][7] != EMPTY_SPACE) or (instructions[current_index][4] == STALL and instructions[stall_issueAtWAW][7] != EMPTY_SPACE and  instructions[stall_issueAtWAR][7] != EMPTY_SPACE):

            stall_issue = waitingRows(current_row, current_index, 4, pipeline_hazard)
           
            #if the pipeline hazard is occuring in row closer to the current row compared to other hazards
            if is_stalling and stall_issue > stall_issueAtWAW and stall_issue > stall_issueAtWAR:

                #updates due to stalling
                instructions[current_index][4] = str(int(instructions[stall_issue][7]) + 1 )
                
                #resets currently stalling
                is_stalling = False
 
                #resets stalling at Write back
                stall_WB = -1
                
            #stalling due to WAW or WAR or RAW hazard
            elif stalling_due_to_WAW or stalling_due_to_WAR or stalling_due_to_RAW:
                
                if stall_issueAtWAW > stall_issueAtWAR and stall_issueAtWAW > stall_issueAtRAW:

                    if instructions[stall_issueAtWAW][7] != EMPTY_SPACE:
                        #updates due to stalling
                        instructions[current_index][4] = str(int(instructions[stall_issueAtWAW][7]) + 1)

                        stalling_due_to_WAW = False
                        stall_issueAtWAW = -1

                        stalling_due_to_WAR = False
                        stall_issueAtWAR = -1

                        stalling_due_to_RAW = False
                        stall_issueAtRAW = -1

                elif stall_issueAtWAR > stall_issueAtWAW and stall_issueAtWAR > stall_issueAtRAW:
                   
                    if instructions[stall_issueAtWAR][7] != EMPTY_SPACE:
                        
                        #updates due to stalling
                        instructions[current_index][4] = str(int(instructions[stall_issueAtWAR][7]) + 1)

                        stalling_due_to_WAR = False
                        stall_issueAtWAR = -1

                        stalling_due_to_WAW = False
                        stall_issueAtWAW = -1

                        stalling_due_to_RAW = False
                        stall_issueAtRAW = -1

                else:
                    if instructions[stall_issueAtRAW][7] != EMPTY_SPACE:
                        
                        #updates due to stalling
                        instructions[current_index][4] = str(int(instructions[stall_issueAtRAW][7]) + 1)

                        stalling_due_to_WAR = False
                        stall_issueAtWAR = -1

                        stalling_due_to_WAW = False
                        stall_issueAtWAW = -1

                        stalling_due_to_RAW = False
                        stall_issueAtRAW = -1

        #Pipeline is busy 
        elif pipeline_busy == True:

            instructions[current_index][4] = STALL
            current_row[4] = STALL

            #index of row waiting in instructions
            stall_issue = waitingRows(current_row, current_index, 4, pipeline_hazard)
            is_stalling = True

        #checks for hazards
        elif waw(current_index,instruction) or war(current_index, instruction): 
            
            #WAW hazard            
            if waw(current_index,instruction):
                instructions[current_index][4] = STALL
                current_row[4] = STALL

                #index of row waiting in instructions
                stall_issueAtWAW = waitingRows(current_row, current_index, 4, WAW_STALL)
                stalling_due_to_WAW = True

            #WAR hazard
            if war(current_index, instruction):
                instructions[current_index][4] = STALL
                current_row[4] = STALL
                
                #index of row waiting in instructions
                stall_issueAtWAR = waitingRows(current_row, current_index, 4, WAR_STALL)
                stalling_due_to_WAR = True

            #RAW hazard
            if raw(current_index, instruction):
                instructions[current_index][4] = STALL
                current_row[4] = STALL
                
                #index of row waiting in instructions
                stall_issueAtRAW = waitingRows(current_row, current_index, 4, RAW_STALL)
                stalling_due_to_RAW = True
                
        elif instructions[current_index][4] == EMPTY_SPACE:
            instructions[current_index][4] = str(int(instructions[current_index-1][4]) + 1)
            
    # AT READ STAGE
    elif empty_index == 5:
        
        instruction = current_row[0]

        if instructions[current_index][4] != STALL:
                
            #there isn't a RAW hazard --> row_not_full
            if not(raw(current_index, instruction)):
                
                instructions[current_index][5] = str(int(instructions[current_index][4]) + 1)

            else:
                #isn't already stalling
                if instructions[current_index][5] != STALL:
                    instructions[current_index][5] = STALL
                    current_row[5] = STALL
                    stall_read = waitingRows(current_row, current_index, 5, EMPTY_SPACE)

                #stalling but ready to read
                elif instructions[current_index][5] == STALL:

                    stall_read = waitingRows(current_row, current_index, 5, EMPTY_SPACE)
                    if(instructions[stall_read][7] != EMPTY_SPACE) and (instructions[stall_read][7] != STALL):
                        instructions[current_index][5] = str(int(instructions[stall_read][7]) + 1)
                        stall_read = -1

                        #weird case
                        if int(instructions[current_index][5]) <= int(instructions[current_index][4]):
                            instructions[current_index][5] = str(int(instructions[current_index][5]) + 1)

    # AT EXECUTE STAGE
    elif empty_index == 6:

        if instructions[current_index][6] == EMPTY_SPACE:
            instruction = instructions[current_index][0]

            #loads stores integer adds subtract
            if instruction == LOAD_INST or instruction == STORE_INST or instruction == ADDI_INST or instruction == ADD_INST or instruction == SUB_INST:
                if clock_cycle >= int(instructions[current_index][5]) + INT_LATENCY:

                    instructions[current_index][6] = str(int(instructions[current_index][5]) + INT_LATENCY)

            #ADD.D and SUB.D
            elif instruction == ADDD_INST or instruction == SUBD_INST:
                if clock_cycle >= int(instructions[current_index][5]) + ADD_LATENCY:

                    instructions[current_index][6] = str(int(instructions[current_index][5]) + ADD_LATENCY)

            #MUL.D
            elif instruction == MULD_INST:
                if clock_cycle >= int(instructions[current_index][5]) + MUL_LATENCY:

                    instructions[current_index][6] = str(int(instructions[current_index][5]) + MUL_LATENCY)

            #DIV.D
            elif instruction == DIVD_INST:
                if clock_cycle >= int(instructions[current_index][5]) + DIV_LATENCY:

                    instructions[current_index][6] = str(int(instructions[current_index][5]) + DIV_LATENCY)

    #AT WRITEBACK STAGE
    elif empty_index == 7:

        #read index isn't stalling
        if instructions[current_index][5] != STALL:
            instruction = instructions[current_index][0]

            #no WAR hazard
            if not(war(current_index, instruction)):
                instructions[current_index][7] = str(int(instructions[current_index][6]) + 1)

            elif instructions[current_index][7] != STALL and (stall_read == -1):
                instructions[current_index][7] = STALL
                current_row[7] = STALL
                #get index of waiting row
                stall_read = waitingRows(current_row, current_index, 7, EMPTY_SPACE)

            #stalling but ready to read
            elif instructions[current_index][7] == STALL and instructions[stall_read][5] != EMPTY_SPACE:

                instructions[current_index][7] = str(int(instructions[stall_read][5]) + 1)
                #no prev raw hazard
                stall_read = -1

#gets index of instruction that's stalling
def waitingRows(current_row, current_index, current_stage, stall_type):
    waiting_row = 0

    #stalling at ISSUE STAGE
    if current_stage == 4:
        
        #stall type is pipeline_hazard
        if stall_type == pipeline_hazard:
            
            for i in range(current_index - 1, Row_not_full-1, -1):

                if (current_row[0] == LOAD_INST or current_row[0] ==ADD_INST or current_row[0] ==ADDI_INST or current_row[0] ==SUB_INST or current_row[0] ==STORE_INST) and instructions[i][0] == LOAD_INST or instructions[i][0]== ADD_INST or instructions[i][0]==ADDI_INST or instructions[i][0]==SUB_INST or instructions[i][0]==STORE_INST:                        
                    waiting_row = i
                    return waiting_row

                elif(current_row[0] == ADDD_INST or current_row[0] == SUBD_INST) and (instructions[i][0]==ADDD_INST or instructions[i][0]==SUBD_INST):
                    waiting_row = i 
                    return waiting_row
                    
        #stalling due to WAW hazard
        elif stall_type == WAW_STALL :
            for i in range(current_index - 1, Row_not_full-1, -1):
                if (instructions[current_index][0] != STORE_INST) and (instructions[i][DEST_REG] == instructions[current_index][DEST_REG]):
                    #if statement that would check if the row is full in terms of a WAR 
                    waiting_row = i
                    return waiting_row

        #stalling due to WAR hazard
        elif stall_type == WAR_STALL:
            for i in range(current_index - 1, Row_not_full-1, -1):
                if (instructions[current_index][0] != STORE_INST) and (instructions[i][SOURCE_ONE] == instructions[current_index][DEST_REG] or instructions[i][SOURCE_TWO] == instructions[current_index][DEST_REG]):
                    waiting_row = i
                    return waiting_row

        #stalling due to RAW hazard
        elif stall_type == RAW_STALL:
            for i in range(current_index - 1, Row_not_full-1, -1):
                if (instructions[current_index][0] != STORE_INST) and (instructions[i][DEST_REG] == instructions[current_index][SOURCE_ONE] or instructions[i][DEST_REG] == instructions[current_index][SOURCE_TWO]):
                    waiting_row = i
                    return waiting_row

    #stalling at READ STAGE
    elif current_stage == 5:
        for i in range(current_index - 1, 0 - 1, -1):

            if (instructions[current_index][0] == STORE_INST): 
                if current_row[DEST_REG] == instructions[i][DEST_REG]:
                    waiting_row = i
                    return waiting_row
                
            elif (current_row[SOURCE_ONE] == instructions[i][DEST_REG]) or (current_row[SOURCE_TWO] == instructions[i][DEST_REG]):
                waiting_row = i
                return waiting_row

    #stalling at WRITEBACK STAGE
    elif current_stage == 7:
        for i in range(current_index - 1, 0 - 1, -1):
            if (instructions[current_index][0] != STORE_INST) and ((current_row[DEST_REG] == instructions[i][SOURCE_ONE]) or (current_row[DEST_REG] == instructions[i][SOURCE_TWO])):
                waiting_row = i
                return waiting_row

    return waiting_row


#Checks only the pipeline with multiple FU's
def pipelineBusy(current_row, current_index):

    #CHECKS INTEGER UNIT PIPELINE
    for i in range(current_index - 1, Row_not_full-1, -1):
        if instructions[current_index][0] == LOAD_INST or instructions[current_index][0] == ADD_INST or instructions[current_index][0] ==ADDI_INST or instructions[current_index][0] == SUB_INST or instructions[current_index][0] ==STORE_INST: 
            if instructions[i][0] == LOAD_INST or instructions[i][0] == ADD_INST or instructions[i][0] == ADDI_INST or instructions[i][0] == SUB_INST or instructions[i][0] == STORE_INST:
                return True
                
    #CHECKS THE FP ADD.D && SUB.D PIPELINE
    for i in range(current_index - 1, Row_not_full-1, -1):
        if (instructions[current_index][0] == ADDD_INST) or (instructions[current_index][0] == SUBD_INST):
            if (instructions[i][0] == ADDD_INST) or (instructions[i][0] == SUBD_INST):
                return True
    #NO PIPELINE ISSUES
    return False

#RUNS THE PROGRAM
def start_program():

    global clock_cycle
    global Row_not_full
    global clock_cycle


    while not(boardFull()) :
        clock_cycle += 1
        
        # 0/0 == an error --> Edge case 
        if instructions[0][0] == DIVD_INST:
            raise Exception("Cannot do operation 0/0")
            
        
        #HARDCODING THE FIRST CYCLE
        if clock_cycle == 1:

            instructions[0][4] = "1"

        elif clock_cycle > 1:

            #goes row by row
            for i in range(Row_not_full,len(instructions)):
                current_row = instructions[i]
                previous_issue = instructions[Row_not_full][4]

                #updates clock in specific cases
                if instructions[i][4] == STALL and ((i == Row_not_full) or (stall_issue >= 0 and instructions[stall_issue][7] != EMPTY_SPACE) or (stall_issueAtWAW >= 0 and instructions[stall_issueAtWAW][7] != EMPTY_SPACE)):
                    updateBoard(current_row, i, "No")

                #if it just issued current row at issue stage or issue of prev row is still stalling
                if instructions[Row_not_full][4] == str(clock_cycle) or (i > 1 and instructions[i-1][4] == STALL) or instructions[i][4] == STALL or (previous_issue == STALL and instructions[Row_not_full][4] != STALL):
                    break
                updateBoard(current_row, i, "No")
                
        #updates the rows that aren't full
        if instructions[Row_not_full][7] != EMPTY_SPACE and instructions[Row_not_full][7] !=  STALL:
            Row_not_full += 1

    #prints the registers and its calculated values
    for i in range(len(instructions)):

        #passing in the instruction as well as the current row 
        compute_registers(instructions[i][0], i)

    printBoard()

#MAIN                
def main():
    loadFile()
    start_program()

main()