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
[7]              Get quantity of users
[8]              Compare 1:1 USER
[9]              Compare 1:n USER
[10]             Get user privileges
[11]             Get DSP Module Version Number
[12_0]           Get Comparison Level
[12_1]           Set Comparison Level
[13]             GET UPLOADED IMAGES
[14]             Get Fingerprint Capture Timeout
[14_1]           Set Fingerprint Capture Timeout
[15]             Read System Time
[15_1]           Set System Time
[16]             Get logged user numbers and privileges
['help', 'h']    show this menu
['d', daemon]    Start daemon to read users  in database
['quit', 'q']    QUIT
```
### Todos

 - Write Tests
 - Create functions for manage pictures
 - 

License
----

MIT

**Free Software!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
