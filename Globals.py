import os
import urllib.request
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from platform import system
import getpass

Graphics = os.path.join(os.getcwd(),"Graphics")
System = system()
if System == "Linux": basePath = "/home/{}/.Checkers-Over-IP".format(getpass.getuser())
elif System == "Windows": basePath = os.path.join(os.getenv('APPDATA'),".Checkers-Over-IP")
else: basePath = "/home/{}/.Checkers-Over-IP".format(getpass.getuser())
LastConnectionFile = os.path.join(basePath,"LastConnection.dat")
NoInternet = False
try: myIP =  urllib.request.urlopen('http://bot.whatismyipaddress.com').read().decode(encoding='UTF-8')
except: 
    myIP = False
    NoInternet = True
    print("Could not open internet connection.")
partnerIP = None
mainWindow = None
Signals = {}
Name = "Name"
PartnerName = "Name"
Black_Turn = 0
Red_Turn = 1
Type = None
ColorIAm = None
AppIcon = None
PiecePixmaps = None

