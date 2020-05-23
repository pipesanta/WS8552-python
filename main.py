from WS8552 import WS8552_FingerPrintReader
import serial.tools.list_ports
import serial, time
ports = serial.tools.list_ports.comports()

# UART SERIAL WIRES
# RED   - VCC
# BLACK - GND
# GREEN - TX
# WHITE - RX 

def findReaderPort(deviceName):
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        if(deviceName in desc):            
            return port

Ws8552 = WS8552_FingerPrintReader(str(findReaderPort("USB-Serial Controller")), 19200)
Ws8552.debug = False
Ws8552.info()

print("############## SCRIPT STARTED ########################")
option=""
while not(option in ["q", "Q", "quit", "QUIT", "d", "daemon"]):
    option = raw_input("which comamnd do you want to run? (\"help\" for options)\n")

    # HELP
    if(option in ["h", "H", "help", "HELP"]):
        print("--- ALLOWED COMMANDS ---")        
        print("[2]              Set debug")
        print("[3_0]            Read the addFingerprintMode")
        print("[3_1]            Set addFingerprintMode")        
        print("[4]              Add fingerprint")
        print("[5]              Delete user by userId")
        print("[6]              Delete all users")
        print("[7]              Get Total users number")
        print("[8]              Compare 1:1 User")
        print("[9]              Compare 1:n User")
        print("[10]             Get user Privileges")
        print("[11]             Get  DSP Module Version Number")
        print("[12_0]           Get Comparison Level")
        print("[12_1]           Set Comparison Level")
        print("[13]             GET UPLOADED IMAGES")
        print("[14]             Get Fingerprint capture Timeout")
        print("[14_1]           Set Fingerprint capture Timeout")
        print("[15]             Read System Time")
        print("[15_1]           Set System Time")
        print("[16]             Get logged user numbers and privileges")
        print("['help', 'h']    show this menu")
        print("['d', daemon]    Start daemon" )
        print("['quit', 'q']    QUIT")
    
    # set debug mode
    elif (option == "2"):
        mode = raw_input("1: True; 0: False ==> \n")
        if(mode == "1"): modeBool = True
        elif(mode == "0"): modeBool = False
        else:
            print("OPTION NOT VALID")         
            break
        Ws8552.debug = modeBool
    # Read addFingerprint mode
    elif(option == "3_0"):
        print("RESPONSE ==> {}".format(Ws8552.readFingerprintAddMode()))
    # set addFingerprint mode
    elif(option == "3_1"):
        optionToSet = raw_input("ALLOW REPEAT? ALLOW: 0 ; PROHIBIT: 1 \n")
        if(int(optionToSet) in [0, 1]):
            print("RESPONSE ==> {}".format(Ws8552.setFingerprintAddMode(int(optionToSet)) ))
        else:
            print("[{} Option is not alloweb]".format(optionToSet)) 
    # Add fingerprint
    elif(option == "4"):
        userId = int(raw_input("user id as INT in range [0, 65534]: "))
        privilege =  int(raw_input("user privileges in range [1,3]: "))
        for i in range(1, 4):
	    response = False
            while not(response):
                print("INTENTO NUMERO {}".format(i))
                response = Ws8552.addFingerprint(i, userId, privilege)
            if(response=="ACK_USER_EXIST"):
                print("USER ALREADY EXIST")
                break
        if(response=="ACK_FAIL"):
            print("TH COMMAND FAILED")
        if(response==True):
           print("USER WITH ID: {} AND PRIVILEGE {} HAS BEEN CREATED".format(userId,privilege))
    elif(option == "5"):
        userId = int(raw_input("user id to REMOVE in range [0, 65534]:\n"))
        print("RESPONSE ==> {}".format(Ws8552.deleteUser(userId)))
    elif(option == "6"):
        print("RESPONSE ==> {}".format(Ws8552.deleteAllUSers()))
    # get total users number
    elif(option == "7"):
        print("RESPONSE ==> {}".format(Ws8552.getTotalUserNumber()))
    elif(option == "8"):
        userId = int(raw_input("user id to COMPARE 1:1 in range [0, 65534] \n"))
        print("RESPONSE ==> {}".format(Ws8552.compareOneToOne(userId)))
    elif(option == "9"):
        print("RESPONSE ==> {}".format(Ws8552.compareOneToMany()))
    elif(option == "10"):
        userId = int(raw_input("user id to GET PRIVILEGES in range [0, 65534]\n"))
        print("RESPONSE ==> {} ".format(Ws8552.getUserPrivilege(userId)))
    elif(option == "11"):
        print("RESPONSE ==> {}".format(Ws8552.getDspModuleVersionNumber()))
    elif(option == "12_0"):
        print("RESPONSE ==> {}".format(Ws8552.getComparisonLevel()))
    elif(option == "12_1"):
        level = int(raw_input("[0, 9] which Comparison level to set ?"))
        print("RESPONSE ==> {}".format(Ws8552.setComparisonLevel(level) ))
    elif(option == "13"):
        print("RESPONSE ==> {}".format(Ws8552.getAndUploadImages() ))
    elif(option == "14"):
        print("RESPONSE ==> {}".format(Ws8552.readFingerprintCaptureTimeout()))
    elif(option == "14_1"):
        timeout = int(raw_input("[0, 255] new timeout ?\n"))
        print("RESPONSE ==> {}".format(Ws8552.setFingerPrintCaptureTimeout(timeout) ))
    elif(option == "15"):
        print("RESPONSE ==> {}".format(Ws8552.getSystemTime() ))
    elif(option == "16"):
        print("RESPONSE ==> {}".format(Ws8552.getAllLoggedUserNumberAndPrivileges()))
    # quit from console
    elif( option in ["q", "Q", "quit", "QUIT" ]):
        print("EXITING APPLICATION")
    # not valid option
    else:
        print("[{}] IS NOT A VALID OPTION".format(option))

    print("\n\n")

if(option in ["d", "daemon"]):
    while(1):
        response = Ws8552.compareOneToMany()
        if(response and len(response) == 2 ):
            print("USER ==> {}; privileges: {} ".format(response[0], response[1]) )
        else:
            print("USER ==> {}".format(response))
        
Ws8552.close()
