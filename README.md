Checkers Over IP
-------------------------------------------

My girlfriend and I like to play board games. Being seperated at college makes this a little difficult, so as a fun programming project, I decided to write a checkers game that we could play together. This, as of February 23, 2015, only works if you are not behind a router. This program operates by starting an XMLRPC server on both computers that are used to swap messages and execute moves in the game. It is a very simple setup, but it is just for fun.

###Use:
####Dependencies-

- python 3.4
- PyQt4

####Running-
main.py in the root directory is the main script for the program and will execute via 'python3 main.py' on Mac & Linux and 'python main.py' on Windows from the command line.