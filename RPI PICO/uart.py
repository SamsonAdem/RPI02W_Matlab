from machine import UART, Pin
import time
import struct
import random
import time
import ure
import socket
import network
import micropython
import gc
import os
import machine


OWN_ID = '14'
SSID = 'OptiTrack'
PASSWORD = 'OptiTrack'


# Initialize UART with specified TX and RX pins
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))  # TX on Pin 0, RX on Pin 1

# Initalize the LED
led = machine.Pin("LED", machine.Pin.OUT)


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



def send_floats_as_int16(uart, floats):
    # Convert floats to integers by multiplying by 1000
    int_values = [int(value * 1000) for value in floats]

    # Pack the integers as int16 (2 bytes each)
    packed_data = struct.pack('hhh', *int_values)  # Big-endian format

    # Send the packed data
    uart.write(packed_data)
    print(packed_data)




if __name__ == '__main__':
    UDP = UDP()
    time_start = 0
    while True:
        data = UDP.receive_package()
        co_ordinates = extract_values(data)
        print(co_ordinates)
        send_floats_as_int16(uart, co_ordinates)
        time.sleep(0.01)  # Send the list every second
        
        
        
