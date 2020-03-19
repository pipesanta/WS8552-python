# WS8552-python
Python library to communicate with WS-8552 fingerprint sensor using UART serial comunication protocol.

### python version: Python 2.7.17

### Run it!
```sh
$ python main.py
```

#### Available commands
```sh
[2]              Set debug
[3_0]            Read the addFingerprintMode
[3_1]            Set addFingerprintMode
[4]              Add fingerprint
[5]              Delete user by userId
[6]              Delete all users
[7]              GET TOTAL USER NUMBER
[8]              COMPARE 1:1 USER
[9]              COMPARE 1:n USER
[10]             GET USER PRIVILEGES
[11]             GET DSP MODULE VERSION NUMBER
[12_0]           GET COMPARISON LEVEL
[12_1]           SET COMPARISON LEVEL
[13]             GET UPLOADED IMAGES
[14]             GET FINGERPRINT CAPTURE TIMEOUT
[14_1]           SET FINGERPRINT CAPTURE TIMEOUT
[15]             READ SYSTEM TIME
[15_1]           Set SYSTEM TIME
[16]             GET logged user numbers and privileges
['help', 'h']    show this menu
['d', daemon]    Start daemon to read users  in database
['quit', 'q']    SALIR DE LA APLICACION
```
### Todos

 - Write Tests
 - Create functions for manage pictures
 - 

License
----

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
