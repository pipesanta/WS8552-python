import serial
import time


class WS8552_FingerPrintReader(object):

    # define ACK_SUCCESS 0x00 	//Operation successfully
    # define ACK_FAIL 0x01 		// Operation failed
    # define ACK_FULL 0x04 		// Fingerprint database is full
    # define ACK_NOUSER 0x05 	//No such user
    # define ACK_FIN_EXIST 0x07 	// already exists
    # define ACK_TIMEOUT 0x08 	// Acquisition timeout

    def __init__(self, port, baudrate):
        super(WS8552_FingerPrintReader, self).__init__()
        self.defaultTimeout= 0.3
        self.ser = serial.Serial(port, baudrate, timeout=self.defaultTimeout, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS)        
        self.debug = True

    def info(self):
        print(self.ser)
    
    def prepareForDaemon(self):
        self.ser.timeout = 0
        print("timeout {}".format(self.ser.timeout))

    
    def read_response(self):
        all_output = []
        output = ''
        i = 0
        output = self.ser.read()
        while output != '':
            if i == 0:
                pass
            else:
                output = self.ser.read()
            if output != '':
                all_output.insert(i, output)
            i += 1
        self.ser.flushOutput()
        validResponse = self.validateGenericResponse(all_output)
        if not(validResponse):
            if(self.debug): print("response not valid => --{}--".format(all_output))
            return False
        self.printResponse(all_output)
        return all_output
    
    def readResponseUntil(self, bytesAtEnd, size):
        output = self.ser.read_until(bytesAtEnd, size)
        self.printResponse(output)
        return output

    def validateGenericResponse(self, response):
        result = False
        if(len(response) < 8 ): return False
        firstByte = ord(response[0]) == 0xF5    # 0xF5 mandatory header
        lastByte = ord(response[-1]) == 0xF5    # 0x00 mandatory end response
        result = (firstByte and lastByte)

        return result

    def printRequest(self, request):
        if not(self.debug): return
        data = []
        for byte in request:
            data.append(hex(byte))
        print("[debug] [{} bytes] WRITING COMMAND: {} ".format(len(data), data) )

    def printResponse(self, response):
        if not(self.debug): return
        data = []
        for byte in response:
            data.append(hex(ord(byte)))
        print("[debug] [{} bytes] RESPONSE: {}".format(len(data), data))

    def send_request(self, cmd, parameters):
        ver = 0x00
        buf = []
        buf.insert(0, 0xF5)				    # Command head
        buf.insert(1, cmd)					# Command
        buf.insert(2, parameters[0])		# parameter 1
        buf.insert(3, parameters[1])		# parameter 2
        buf.insert(4, parameters[2])		# parameter 3
        buf.insert(5, 0x00)			        # 0 before CHK

        for i in range(1, 6):
            ver = ver ^ buf[i]

        buf.insert(6, ver)					# CHK
        buf.insert(7, 0xF5) 				# end of command

        self.printRequest(buf)
        self.ser.write(buf)
        self.ser.flushInput()

    def printOnDebug(self, msj):
        if(self.debug):
            print(msj)

    # Enable the module into a dormant state (Both command and response are 8 bytes)
    def enableDormantState(self):
        if(self.debug): print("## ENABLING DORMAN STATE ##")
        # self.send_request(0X2C, [0x00, 0x00, 0x00])
        # response = self.read_response()
        # return response

    # Read the fingerprint add mode (Both command and response are 8 bytes)
    def readFingerprintAddMode(self):
        if(self.debug): print("Reading fingerprint add mode")
        self.send_request(0x2D, [0x00, 0x00, 0x01])
        response = self.readResponseUntil([0xF5], 8)
        if not(response): return False 
        ackByte = ord(response[4])
        # Verify response
        if( ackByte == 0x01):
            print("ACK FAILED")
            return
        elif(ackByte == 0x00):
            mode = ord(response[3])
            if(mode == 0x00):
                return "ALLOW_REPEAT"
            elif(mode == 0x01):
                return "PROHIBIT_REPEAT"

    # Set the fingerprint add mode (Both command and response are 8 bytes)
    def setFingerprintAddMode(self, mode):
        ''' 0x00 ALLOW, 0x01 PROHIBIT '''
        if(self.debug): print("setting fingerprint add mode: {}".format(mode))
        self.send_request(0x2D, [0x00, mode, 0x00])
        response = self.readResponseUntil([0xF5], 8)
        # Verify response        
        successByte = ord(response[4])
        if(successByte == 0x01):
            print ("readFingerprintAddMode operation failed")
            return False
        elif(successByte == 0x00):
            return True

    # To ensure the effectiveness, user must input a fingerprint three times, the host is required to send command to the
    # DSP module three times.
    def addFingerprint(self, time, userid, userPrivilege):
        '''
        Range of user number is 1 - 0xFFF;
        Range of User privilege is 1, 2, 3, its meaning is defined by secondary developers themselves.
        '''
        self.printOnDebug("Adding fingerprint #{} with userId {}, with privilege level {}".format(time, userid, userPrivilege))
        if not(userPrivilege in [1,2,3]):
            self.printOnDebug("User privilege is not allowed")
            return False
        self.ser.timeout = None
        userIdAsBinary = format(userid, '016b')

        p1 = userIdAsBinary[0: 8]
        p2 = userIdAsBinary[8: 16]
        self.send_request(time, [ int(p1, 2), int(p2, 2), userPrivilege ])
        response = self.readResponseUntil([0xF5], 8)
        self.ser.timeout = self.defaultTimeout
        validResponse = False
        if (len(response) == 0): 
            self.printOnDebug("DATA RESPONSE IS EMPTY")
            return False
        ackByte = ord(response[4])
        if(len(response) == 8 and ackByte == 0x01 ): self.printOnDebug("FAILED ACK")
        if(len(response) == 8 and ackByte == 0x00 ): validResponse = True
        return validResponse

    # Delete specified user (Both command and response are 8 bytes)
    def deleteUser(self, userId):
        self.printOnDebug("DELETING USER {}".format(userId))
        userIdAsBinary = format(userId, '016b')
        p1 = userIdAsBinary[0: 8]
        p2 = userIdAsBinary[8: 16]
        self.send_request(0x04, [int(p1, 2), int(p2, 2), 0x00])

        response = self.readResponseUntil([0xF5], 8)
        validResponse = False
        
        if not(len(response) == 8): return False

        ackByte = ord(response[4])
        if(ackByte == 0x01): self.printOnDebug("FAILED ACK")
        if(ackByte == 0x05): self.printOnDebug("NO SUCH USER")
        if(ackByte == 0x00): validResponse = True
        return validResponse
    
    # Delete all users (Both command and response are 8 bytes)
    def deleteAllUSers(self):
        if(self.debug): print("DELETING ALL USERS")
        self.send_request(0x05, [0x00, 0x00, 0x00])
        response = self.readResponseUntil([0xF5], 8)
        
        if not(len(response) == 8): return False 
        return ord(response[4]) == 0x00
    
    # Acquire the total number of users (Both command and response are 8 bytes)
    def getTotalUserNumber(self):
        if(self.debug): print("Calling getTotalUserNumber")
        self.send_request(0x09, [0x00, 0x00, 0x00])
        result = self.readResponseUntil([0xf5], 8)
        # Verify response
        
        if not (len(result) == 8): return False 
        numberAsBinary = "".join([
            format(ord(result[2]), '08b'),
            format(ord(result[3]), '08b')
        ])
        responseAsInt = int(numberAsBinary, 2)
        return responseAsInt
    
    # Compare 1:1 (Both command and response are 8 bytes)
    def compareOneToOne(self, userId):
        if(self.debug): print("COMPARING 1:1 UserID: {}".format(userId))
        self.ser.timeout = None
        userIdAsBinary = format(userId, '016b')
        p1 = userIdAsBinary[0: 8]
        p2 = userIdAsBinary[8: 16]

        self.send_request(0x0B, [int(p1, 2), int(p2, 2), 0x00])
        response = self.readResponseUntil([0xF5], 8)
        
        if not(len(response) == 8):
            self.printOnDebug("RESPONSE HAS N0T 8 BYTES")
            return False
        switcher = { 0: True, 1: "ACK FAIL", 5: "NOT SUCH USER"}
        self.ser.timeout = self.defaultTimeout
        return switcher.get(ord(response[4]))

    # Compare 1: N (Both command and response are 8 bytes)
    def compareOneToMany(self):
        if(self.debug): print("COMPARING 1: N")
        self.ser.timeout = None
        self.send_request(0x0C, [0x00, 0x00, 0x00])
        response = self.readResponseUntil([0xF5], 8)
        self.ser.timeout = self.defaultTimeout
        
        byte4 = ord(response[4])
        if(byte4 == 0x05 ):
            self.printOnDebug("NO SUCH USER")
            return ["NO SUCH USER"]
        if(byte4 == 0x08):
            self.printOnDebug("ACK TIMEOUT")
            return ["ACK TIMEOUT"]
        if(byte4 in [0x01, 0x02, 0x03]):
            ## hex to int
            byte2 = format(ord(response[2]), '08b')
            byte3 = format(ord(response[3]), '08b')
            userId = int( "".join([byte2,  byte3]), 2 )
            return [userId, byte4]        
        return False

    # Acquire user privilege (Both command and response are 8 bytes)
    def getUserPrivilege(self, userId):
        if(self.debug): print("Getting privileges of user with id: {}".format(userId))
        userIdAsBinary = format(userId, '016b')
        p1 = userIdAsBinary[0: 8]
        p2 = userIdAsBinary[8: 16]
        self.send_request(0x0A, [int(p1, 2), int(p2, 2), 0x00])
        response = self.readResponseUntil([0xF5], 8)
        
        if not(len(response) == 8): 
            self.printOnDebug("response size is {}, 8 was expected ".format(len(response)))
            return False
        byte4 = ord(response[4])
        if( byte4 == 0x05 ): 
            self.printOnDebug("NOT SUCH USER")
            return False
        if(byte4 in [0x01, 0x02, 0x03]):            
            return byte4
        return False
    
    # Acquire DSP module version number (command = 8 bytes, and response > 8 bytes)
    def getDspModuleVersionNumber(self):
        if(self.debug): print("getting DSP module version number")
        self.send_request(0x26, [0x00, 0x00, 0x00])
        response = self.read_response()
        if not(response): return False
        headerResponse = response[0:7]
        dataPackage = response[8:]
        responseAsString = []
        ackByte = ord(headerResponse[4])
        if( ackByte == 0x01 ): 
            if(self.debug): print("ACK FAIL")
            return False
        elif(ackByte == 0x00):
            lenHi  = format(ord(headerResponse[2]), "08b") 
            lenLow = format(ord(headerResponse[3]), "08b")
            lenSize = int( lenHi + lenLow, 2)            
            responseAsString = []
            data = dataPackage[1: (1+lenSize)]
            for byte in data:
                responseAsString.append(chr(ord(byte)))
            return "".join(responseAsString)
        return False

    # Read comparison level (Both command and response are 8 bytes)
    def getComparisonLevel(self):
        if(self.debug): print("Reading Comparison level")
        self.ser.timeout = None
        self.send_request(0x28, [0x00, 0x00, 0x01])
        response = self.readResponseUntil([0xF5], 8)
        self.ser.timeout = self.defaultTimeout
        validResponse = False
        if not(len(response) == 8):
            self.printOnDebug("Response size is {}. 8 was expected".format(len(response)))
            return validResponse
        ackByte = ord(response[4])
        if(ackByte == 0x01):
            self.printOnDebug("ACK FAILED")
        elif(ackByte == 0x00):
            return ord(response[3])
        return validResponse
    
    # Set comparison level (Both command and response are 8 bytes)
    def setComparisonLevel(self, level):
        if not(level in [0,1,2,3,4,5,6,7,8,9]):
            self.printOnDebug("[Error] {} level is not allowed".format(level))
            return False
        self.ser.timeout = None
        self.printOnDebug("Setting comparison level. {}".format(level))
        self.send_request(0x28, [0x00, level, 0x00])
        response = self.readResponseUntil([0xF5], 8)
        self.ser.timeout = self.defaultTimeout
        ackByte = ord(response[4])
        return (ackByte == 0x00)

    # Acquire and upload images
    # Acquire and upload images (Command = 8 bytes, response > 8 bytes)
    def getAndUploadImages(self):
        self.printOnDebug("Getting uploaded images... ")
        self.ser.timeout = 3
        self.send_request(0x24, [0x00, 0x00, 0x00])
        response = self.read_response()

        if not(response): return False
        headerResponse = response[0:7]
        dataPackage = response[8:]
        responseAsString = []
        ackByte = ord(headerResponse[4])
        if( ackByte == 0x01 ): 
            self.printOnDebug("ACK FAIL")
            return False
        elif(ackByte == 0x08):
            self.printOnDebug("TIMEOUT")
            return False
        elif(ackByte == 0x00):
            lenHi  = format(ord(headerResponse[2]), "08b") 
            lenLow = format(ord(headerResponse[3]), "08b")
            lenSize = int( lenHi + lenLow, 2)            
            responseAsString = []
            data = dataPackage[1: (1+lenSize)]
            print("dataSize: {}".format(lenSize))
            f = open("image.jpg", "wb")
            for byte in data:
                f.write(byte)
                #responseAsString.append(chr(ord(byte)))
            f.close()
            return "image.jpg"
        return False


    # Upload acquired images and extracted eigenvalue (Command = 8 bytes, and response > 8 bytes)
    def getAllLoggedUserNumberAndPrivileges(self):
        self.printOnDebug("Getting logged users and privileges ")
        self.send_request(0x2B, [0x00, 0x00, 0x00])
        response = self.read_response()
        if not(response): return False
        headerResponse = response[0:7]
        dataPackage = response[8:]
        ackByte = ord(headerResponse[4])
        if(ackByte == 0x01): return
        if(ackByte == 0x00):
            lenHi  = format(ord(headerResponse[2]), "08b") 
            lenLow = format(ord(headerResponse[3]), "08b")
            lenSize = int( lenHi + lenLow, 2)
            responseAsString = []
            data = dataPackage[1: (1+lenSize)]
            print("dataSize: {}".format(lenSize))



        return ackByte



    # Read system time
    def getSystemTime(self):
        self.printOnDebug("Getting system time")
        self.send_request(0x3C, [0x00, 0x00, 0x00])
        response = self.read_response()
        return response

    # Set/read fingerprint capture timeout value (Both command and response are 8 bytes)
    def readFingerprintCaptureTimeout(self):
        '''
        Note:
        Range of fingerprint waiting timeout (tout) value is 0-255. If the value is 0, the fingerprint acquisition process will
        keep continue if no fingerprints press on; If the value is not 0, the system will exist for reason of timeout if no
        fingerprints press on in time tout * T0.
        '''
        self.printOnDebug("Getting Read fingerprintCapture")
        self.send_request(0x2E, [0x00, 0x00, 0x01])
        self.ser.timeout = None
        response = self.readResponseUntil([0xF5], 8)
        if not(len(response) == 8):
            self.printOnDebug("Response size is {}, but 8 was expected".format(len(response)))
            return False
        if(ord(response[4]) == 0x01):
            self.printOnDebug("ACK FAILED")
            return False
        if(ord(response[4]) == 0x00):
            return ord(response[3])

    def setFingerPrintCaptureTimeout(self, timeout):
        self.printOnDebug("Setting fingerprint_capture timeout of {}".format(timeout))
        self.send_request(0x2E, [0x00, timeout, 0x00 ])
        response = self.read_response()
        if(ord(response[4]) == 0x01):
            self.printOnDebug("ACK FAILED")
            return False
        elif(ord(response[4]) == 0x00):
            return True

    def close(self):
        self.ser.close()
