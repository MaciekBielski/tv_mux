Data that are parsed from a Wikipedia page are TV-stations available on 4
DVB-T mutexes in Poland.

Please, keep in mind that this simple program is not secured against weird
commands or arguments, errors (if they appear) are not handled in a
nice way etc. Some checkings are implemented but you should use proper commands
and than it will work correctly. This was only student project, not
professional industry software. Have fun!

===============================================================================
AVAILABLE COMMANDS:

LS - ('local show') - print local data parsed from the page
RS - ('remote show') - print the data stored in database
ADD [indices] - add chosen local rows to the database
DEL [indices] - delete chosen rows from the database
DROP - clean the database
Q - quit the program

- The same record will be never added twice!
- If a record with some id is not in the database then it's deletion will have
  no effect.
- Ranges and element for ADD/DEL can overlap, they will be used only once.

EXAMPLE USAGE:

Open a shell window, go to directory with this file and first run server:
$ python3 muxServer.py
Then open another shell window and run client:
$ python3 muxClient.py

All the time you will operate in client's window, obviously. After starting
the program you should be presented with a prompt "><>".  First, make sure,
that the program has parsed a given page and retrieved the data. In order to
do so run:
><> LS
which should list all the data that client has got from the network. At the
beginning there is no data kept at the server side. If only the header row
will be presented try to close a client (type "Q") and start again. That means
that something bad happened during connecting with the Internet.

If you have a data locally now you can store some of them on the server.
Choose rows to store by specifying theirs' indices:
><> ADD 4-10, 15-25, 27
You can use ranges or a single values but you have to divide them by a comma.

Now you can check what's in your database:
><> RS
That will print you all the rows that are currently stored in your database.
Rows parsed by the client program are only stored locally. Any data stored by
the server will persist as long as the server is running (no file storage or
external database system for simplicity)

If you want to delete some rows from the database try:
><> DEL 6-8,11,17
><> RS

Or you can clean the whole database memory by:
><> DROP

In order to quit, type:
><> Q

===============================================================================
PROGRAM FLOW AND PROTOCOL:

prompt -> input -> exeCmd() -> corresponding function returns:
  - command for the server: reqStr
  - binary data (if applicable to a give command): reqData
  - callback function that will be called when a response will arrive

-> sendMsg transforms reqStr and reqData to the format:
  <command>\n
  <data length>\n
  <data>
  and sends it as a binary via socket (using file-like socket handler: fs)

-> receiveMsg gets the anser from a socket, analyze it and returns respMsg
  (string) and respData (binary)

-> callback is invoked with respData as an argument

- Both functions sendMsg and receiveMsg are working symmetric, form client and
  server point of view.
- Once a socket is connected it is accessed by file-like handler which is
  automatically closed when exiting 'with (...) as fs:' block. This is very
  handy but you have to remember to call fs.flush() after each writing. Only
  then it works correctly.
- When records (MuxChannel objects) are sent over the socket first they are
  pickled in order to obtain binary format. Bunch of records is sent as
  bytearray.

===============================================================================
IMPLEMENTATION:

This software has been created and tested with Python 3.4.2. Probably it may
not run properly on Python2 without modifications.

In muxCommon.py you can find one class - object row and functions shared by
both server and client.

In muxClient.py first part is a class of parser object, which retrieves the
data from the webpage and use them to build an MuxChannel object - data record.
The next function is in charge of obtaining the body of the page.
After that you can find few functions called accordingly to the user command,
another function that interprets the user's command. The last one is a
function responsible for interaction with a user.

Analogically, you can find function corresponding to particular commands
in muxServer.py

You can find some comments in source code.
