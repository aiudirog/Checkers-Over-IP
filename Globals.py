import os
import urllib.request
from PyQt4.QtCore import *
from PyQt4.QtGui import *

Graphics = os.path.join(os.getcwd(),"Graphics")
LastConnectionFile = os.path.join(os.getcwd(),"LastConnection.dat")
myIP =  urllib.request.urlopen('http://bot.whatismyipaddress.com').read().decode(encoding='UTF-8')
partnerIP = None
mainWindow = None
Signals = {}
Name = "Name"
