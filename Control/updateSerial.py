# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 21:46:09 2022

@author: Ralf
"""

import time
import sys
import serial
import io

from threading import Thread

class updateSerial():
    def __init__(self):
        
        #Check for available COMports
        #prts = serial.tools.list_ports.comports()
        
        
        
        #define serial parts
        
        
    def serialStart(self):
        
        #Add code to start serial comms
        
    def serialDataSend(self):
        
        #Add code to take all current manual MEMS values and send string to Arduino
        
    def serialDataSendOne(self):
        
        #Add code to take values from defined table + frame number and times and send to Arduino
        
    def serialDataSendThree(self):
        
        #Add codet to take values from defined table + frame number and times and send to Arduino
        
    def closeSerial(self):
        
        #Add code to close serial connection