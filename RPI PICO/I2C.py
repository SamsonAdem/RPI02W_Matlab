from i2c_responder import I2CResponder
import random
import time
import ure
import struct
import socket
import time
import network
import micropython
import gc
import os
import machine


led = machine.Pin("LED", machine.Pin.OUT)

OWN_ID = '14'
SSID = 'OptiTrack'
PASSWORD = 'OptiTrack'

def extract_values(message):
    values = [] 
    for i in range(len(message)): 
        if message[i] == 'X':
            x = i
        elif message[i] == 'Y':
            y = i
        elif message[i] == 'Z':
            z = i
        elif message[i] == 'N':
            n  = i
    x_values = values.append(float(message[x+1:y]))
    y_values = values.append(float(message[y+1:z]))
    z_values = values.append(float(message[z+1:n]))
    return values


class UDP():
    def __init__(self):
        self.MCAST_GRP = '224.1.5.16'
        self.MCAST_PORT = 9242
        self.setup_wifi()
        self.setup_UDP()
        self.pos = {}

    def inet_aton(self,addr):
        return(bytes(map(int, addr.split("."))))

    def setup_wifi(self):
        print("Connection to OptiTrack Wifi")
        wifi=network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi.config(pm = 0xA11142) #Turn of power save mode, for lower ping 0xA11142 eller 0xA11140 to disable power saving
        wifi.connect(SSID,PASSWORD, channel = 48) #Remove/add channel = XX if not working

        while wifi.isconnected()==False:
            print('Waiting for connection')
            time.sleep(1)
        time_connected = time.time()
        wifiInfo=wifi.ifconfig()
        self.ServerIP=wifiInfo[0]
        led.off()
        led.on()
        print(f"printting own IP: {self.ServerIP}")	

        #Setup listing to multicast
    def setup_UDP(self):
        print("Start listening to multicast on '224.1.5.16' port 9242")
        MCAST_GRP = '224.1.5.16'
        MCAST_PORT = 9242

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,  self.inet_aton(self.MCAST_GRP) + self.inet_aton(self.ServerIP)) #ServerIP is own IP
        self.sock.bind((self.MCAST_GRP, self.MCAST_PORT))
        return self.sock
    
    def decode_message(self,message):
        message = message.split("#")
        for txt in message:
            if len(txt)>=2:
                if txt[0:2] == "ID":
                    ID = txt[2:]
                    self.pos[ID]={}
                elif txt[0:2] == "PX":
                    self.pos[ID]["PX"] = txt[2:]
                elif txt[0:2] == "PY":
                    self.pos[ID]["PY"] = txt[2:]
                elif txt[0:2] == "PZ":
                    self.pos[ID]["PZ"] = txt[2:]              
                    
    
    def receive_package(self):
        data, address = self.sock.recvfrom(1024)
        data = data.decode("utf-8")
        return data
    

class I2C_custom():
    def __init__(self):
        self.RESPONDER_I2C_DEVICE_ID = 0
        self.RESPONDER_ADDRESS = 0x41
        self.GPIO_RESPONDER_SDA = 4
        self.GPIO_RESPONDER_SCL = 5
        
        self.i2c_responder = I2CResponder(
            self.RESPONDER_I2C_DEVICE_ID, sda_gpio=self.GPIO_RESPONDER_SDA, scl_gpio=self.GPIO_RESPONDER_SCL, responder_address=self.RESPONDER_ADDRESS
        )

    def i2c_send_int(self, data):
        # Ensure data is a list of integers
        if not all(isinstance(i, int) for i in data):
            raise ValueError("All elements in data must be integers")
       
        
        print("Sending I2C data. Will wait for master to be ready to receive")
        for value in data:
            # I2C READ.
            while not self.i2c_responder.read_is_pending():
                pass
            self.i2c_responder.put_read_data(value)
            
    def i2c_send_float(self, data):
        # Ensure data is a list of floats
        if not all(isinstance(i, float) for i in data):
            raise ValueError("All elements in data must be floats")
    
        
        all_bytes = b''.join(struct.pack('f', value) for value in data)
        send_byte = list(all_bytes)
        I2C_module.i2c_send_int(list(all_bytes))
        
    def i2c_send(self, data):
        #Translate data into something that can be send over I2C
        values = []
        for char in data:
            values.append(ord(char))      
        print("Sending I2C data. Will wait for master to be ready to receive")
        for value in values:
        # I2C READ.
            while not self.i2c_responder.read_is_pending():
                pass
            #print(chr(value))
            self.i2c_responder.put_read_data(int(value))

        




        

if __name__ == '__main__':
#     UDP = UDP()
    I2C_module = I2C_custom()
    time_start = time.time()
    while True:
#         data = UDP.receive_package()
#         co_ordinates = extract_values(data)
        I2C_module.i2c_send("3.232,2.333,4.567")

    


