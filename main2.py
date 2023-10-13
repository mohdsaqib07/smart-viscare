from win32api import GetLastInputInfo,GetTickCount
import time 

n=input("Enter a number : ")
time.sleep(10)
print((GetTickCount() - GetLastInputInfo()) // 1000)
print(n)