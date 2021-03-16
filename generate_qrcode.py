# Generate QrCode Using Python
import pyqrcode # pip install pyqrcode
import png # pip install pypng
from pyqrcode import QRCode

QRstring = "www.google.com.br" # paste any url here
url = pyqrcode.create(QRstring) # creates the QRCode 
url.png(r'C:\Users\Guga\Desktop\qr_code.png', scale = 8) # saves the QRCode image

# Other different destination path syntax:
#url.png('C:/Users/Guga/Desktop/qr_code.png', scale = 8) 
#url.png('C:\\Users\\Guga\\Desktop\\qr_code.png', scale = 8)



