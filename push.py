import os

message = input("Commit message: ")

os.system("git add -A")
os.system("git commit -m '"+message+"'")
os.system("git push")
