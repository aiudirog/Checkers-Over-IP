import os
import urllib.request
import urllib.error
import socket
from platform import system
import getpass

# Identify graphics folder
Graphics = os.path.join(os.getcwd(), "Graphics")

# Identify OS and get application data folder
System = system()
if System == "Linux":
    basePath = "/home/{}/.Checkers-Over-IP".format(getpass.getuser())
elif System == "Windows":
    basePath = os.path.join(os.getenv('APPDATA'), ".Checkers-Over-IP")
else:
    basePath = "/home/{}/.Checkers-Over-IP".format(getpass.getuser())

# Get information on the last connection, like your name, IP address of server, etc.
LastConnectionFile = os.path.join(basePath, "LastConnection.dat")

# Test for internet, enter offline mode if not found.
NoInternet = False
try:
    myIP = urllib.request.urlopen('http://bot.whatismyipaddress.com').read().decode(encoding='UTF-8')
except (socket.gaierror, urllib.error.URLError):
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
Current_Turn = 1
Type = None
ColorIAm = None
AppIcon = None
PiecePixmaps = {
    10: None,  # black_unselected_pixmap
    20: None,  # red_unselected_pixmap
    11: None,  # black_selected_pixmap
    21: None,  # red_selected_pixmap
    110: None,  # black_king_unselected_pixmap
    120: None,  # red_king_unselected_pixmap
    111: None,  # black_king_selected_pixmap
    121: None,  # red_king_selected_pixmap
    1: None,  # selected
    0: None,  # clear
    1010: None,  # black_last_selected_pixmap
    1020: None,  # red_last_selected_pixmap
    1110: None,  # black_king_last_selected_pixmap
    1120: None,  # red_king_last_selected_pixmap
}
