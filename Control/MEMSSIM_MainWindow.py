# -*- coding: utf-8 -*-
"""
Created on Wed Nov 3 14:12:00 2021

@author: Ralf
"""
import sys, csv

from PyQt5 import QtCore, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QMainWindow, QApplication, QButtonGroup, QTableWidgetItem

from MEMSSIM_UI import Ui_MainWindow

#from stack overflow: https://stackoverflow.com/questions/55078698/implement-a-select-port-function-from-combobox
class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.portname_comboBox = QtWidgets.QComboBox()
        self.baudrate_comboBox = QtWidgets.QComboBox()

        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.portname_comboBox.addItem(info.portName())

        for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
            self.baudrate_comboBox.addItem(str(baudrate), baudrate)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lay = QtWidgets.QFormLayout(self)
        lay.addRow("Port Name:", self.portname_comboBox)
        lay.addRow("BaudRate:", self.baudrate_comboBox)
        lay.addRow(buttonBox)
        self.setFixedSize(self.sizeHint())

    def get_results(self):
        return self.portname_comboBox.currentText(), self.baudrate_comboBox.currentData()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.MEMSmidValue = 25000
        self.startMark = '<'
        self.endMark = '>'
        self.priorValue1Pos = ['0']*((8*3)+3)
        self.priorValue3Pos = ['0']*((8*9)+3)
        
        self.connectArduino.clicked.connect(self.openDialog)
        self.disconnectArduino.clicked.connect(self.disconArduino)
        
        self.pushButton_saveTable.clicked.connect(self.handleSave)
        self.pushButton_openTable.clicked.connect(self.handleOpen)
        self.pushButton_openTableGreen660.clicked.connect(self.handleOpenG660)
        self.pushButton_openTableGreen550.clicked.connect(self.handleOpenG550)
        self.pushButton_openTableGreen440.clicked.connect(self.handleOpenG440)
        self.pushButton_openTableGreen330.clicked.connect(self.handleOpenG330)
        self.pushButton_openTableBlue660.clicked.connect(self.handleOpenB660)
        self.pushButton_openTableBlue550.clicked.connect(self.handleOpenB550)
        self.pushButton_openTableBlue440.clicked.connect(self.handleOpenB440)
        self.pushButton_openTableBlue330.clicked.connect(self.handleOpenB330)

#M1 manual slider change Signals############################################################################################
        
        self.sliderM1_phase.valueChanged['int'].connect(self.M1Phase)
        self.sliderM1_x.valueChanged['int'].connect(self.M1x)
        self.sliderM1_y.valueChanged['int'].connect(self.M1y)
        
        self.sliderM1_phase.sliderPressed.connect(self.sldDisconnect)
        self.sliderM1_phase.sliderReleased.connect(self.sldReconnectM1_phase)
        self.sliderM1_x.sliderPressed.connect(self.sldDisconnect)
        self.sliderM1_x.sliderReleased.connect(self.sldReconnectM1_x)        
        self.sliderM1_y.sliderPressed.connect(self.sldDisconnect)
        self.sliderM1_y.sliderReleased.connect(self.sldReconnectM1_y)        
#M2 manual slider change Signals############################################################################################
        
        self.sliderM2_phase.valueChanged['int'].connect(self.M2Phase)
        self.sliderM2_x.valueChanged['int'].connect(self.M2x)
        self.sliderM2_y.valueChanged['int'].connect(self.M2y)

        self.sliderM2_phase.sliderPressed.connect(self.sldDisconnect)
        self.sliderM2_phase.sliderReleased.connect(self.sldReconnectM2_phase)
        self.sliderM2_x.sliderPressed.connect(self.sldDisconnect)
        self.sliderM2_x.sliderReleased.connect(self.sldReconnectM2_x)        
        self.sliderM2_y.sliderPressed.connect(self.sldDisconnect)
        self.sliderM2_y.sliderReleased.connect(self.sldReconnectM2_y)         
#simple control to only allow single position when 1-pos automated########################################

        self.bg = QButtonGroup()
        self.bg.addButton(self.checkBox_pos1,1)
        self.bg.addButton(self.checkBox_pos2,2)
        self.bg.addButton(self.checkBox_pos3,3)
        
#automated runs######################################################################################

        self.pushButton_Auto1Pos.clicked.connect(self.auto1Pos)
        self.pushButton_Auto3Pos.clicked.connect(self.auto3Pos)
        
#Close program############################################################################################
        
        self.pushButton_close.clicked.connect(self.closeProg)
        
#define serial connection#################################################################################
        
        self.serial = QtSerialPort.QSerialPort(
            self,
            readyRead=self.serialReceive
        )
        
#initialise table###################################################################################
        for i in range(9):
            for j in range(8):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.MEMSmidValue)))
                
        self.pushButton_setP1_1.clicked.connect(self.setP11)
        self.pushButton_setP1_2.clicked.connect(self.setP12)
        self.pushButton_setP1_3.clicked.connect(self.setP13)
        self.pushButton_setP2_1.clicked.connect(self.setP21)
        self.pushButton_setP2_2.clicked.connect(self.setP22)
        self.pushButton_setP2_3.clicked.connect(self.setP23)
        self.pushButton_setP3_1.clicked.connect(self.setP31)
        self.pushButton_setP3_2.clicked.connect(self.setP32)
        self.pushButton_setP3_3.clicked.connect(self.setP33)
        
        self.pushButton_moveP1_1.clicked.connect(self.M11PosSet)
        self.pushButton_moveP1_2.clicked.connect(self.M12PosSet)
        self.pushButton_moveP1_3.clicked.connect(self.M13PosSet)
        self.pushButton_moveP2_1.clicked.connect(self.M21PosSet)
        self.pushButton_moveP2_2.clicked.connect(self.M22PosSet)
        self.pushButton_moveP2_3.clicked.connect(self.M23PosSet)
        self.pushButton_moveP3_1.clicked.connect(self.M31PosSet)
        self.pushButton_moveP3_2.clicked.connect(self.M32PosSet)
        self.pushButton_moveP3_3.clicked.connect(self.M33PosSet)
####################################################################################################################        
#Value change methods###############################################################################################
    
    def openDialog(self):
        dialog = Dialog()
        if dialog.exec_():
            portname, baudrate = dialog.get_results()
            self.serial.setPortName(portname)
            self.serial.setBaudRate(baudrate)
            self.portNameText.setText(portname)
            self.baudRateText.setText(str(baudrate))
            self.serial.open(QtCore.QIODevice.ReadWrite)
            self.connectedBtn.setChecked(True)
            
    def disconArduino(self):
        self.serial.close()
        self.connectedBtn.setChecked(False)
        
    def serialDataSend(self):
        #udpate DAC values manually
        currentValue = [0]*8
        currentValue[0] = self.spinBox_M1_1.value()
        currentValue[1] = self.spinBox_M1_2.value()
        currentValue[2] = self.spinBox_M1_3.value()
        currentValue[3] = self.spinBox_M1_4.value()
        currentValue[4] = self.spinBox_M2_1.value()
        currentValue[5] = self.spinBox_M2_2.value()
        currentValue[6] = self.spinBox_M2_3.value()
        currentValue[7] = self.spinBox_M2_4.value()
        currentValueText = [str(element).zfill(5) for element in currentValue]
        
        textToSend = self.startMark + ",".join(currentValueText) + self.endMark
        print(textToSend)
        self.serial.write(textToSend.encode())
            
    def serialReceive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.lineEdit_receivedSerial.setText(text)
            print(text)
            
    def auto1Pos(self):
        #Code for sending instruction for auto 1 pos bit
        currentValue = ['0']*((8*3)+3)
        frameNo = self.spinBox_frameNo1Pos.value()
        expTime = self.spinBox_ExposureTime1Pos.value()
        waitTime = self.spinBox_WaitTime1Pos.value()
        jj = 0
        if self.checkBox_pos1.isChecked():
            for i in range(3):
                for j in range(8):
                    currentValue[jj] = self.tableWidget.item(i,j).text().zfill(5)
                    jj += 1
        if self.checkBox_pos2.isChecked():
            for i in range(3,6):
                for j in range(8):
                    currentValue[jj] = self.tableWidget.item(i,j).text().zfill(5)
                    jj += 1
        if self.checkBox_pos3.isChecked():
            for i in range(6,9):
                for j in range(8):
                    currentValue[jj] = self.tableWidget.item(i,j).text().zfill(5)
                    jj += 1
        currentValue[jj] = str(frameNo).zfill(3)
        currentValue[jj+1] = str(expTime).zfill(3)
        currentValue[jj+2] = str(waitTime).zfill(3)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        
    def auto3Pos(self):
        #code for sending instruction to arduino for fully auto
        currentValue = ['0']*((8*9)+3)
        frameNo = self.spinBox_frameNo3Pos.value()
        expTime = self.spinBox_ExposureTime3Pos.value()
        waitTime = self.spinBox_WaitTime3Pos.value()
        jj = 0
        for i in range(9):
            for j in range(8):
                currentValue[jj] = self.tableWidget.item(i,j).text().zfill(5)
                jj += 1
        currentValue[jj] = str(frameNo).zfill(3)
        currentValue[jj+1] = str(expTime).zfill(3)
        currentValue[jj+2] = str(waitTime).zfill(3)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())

    def M11PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(0,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(0,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(0,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(0,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(0,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(0,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(0,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(0,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(0,7).text()))
        print(textToSend)

    def M12PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(1,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(1,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(1,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(1,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(1,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(1,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(1,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(1,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(1,7).text()))
        print(textToSend)

    def M13PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(2,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(2,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(2,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(2,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(2,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(2,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(2,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(2,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(2,7).text()))
        print(textToSend)

    def M21PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(3,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(3,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(3,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(3,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(3,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(3,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(3,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(3,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(3,7).text()))
        print(textToSend)

    def M22PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(4,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(4,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(4,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(4,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(4,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(4,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(4,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(4,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(4,7).text()))
        print(textToSend)

    def M23PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(5,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(5,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(5,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(5,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(5,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(5,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(5,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(5,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(5,7).text()))
        print(textToSend)

    def M31PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(6,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(6,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(6,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(6,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(6,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(6,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(6,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(6,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(6,7).text()))
        print(textToSend)

    def M32PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(7,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(7,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(7,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(7,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(7,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(7,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(7,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(7,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(7,7).text()))
        print(textToSend)

    def M33PosSet(self):
        currentValue = ['0']*((8*1))
        for j in range(8):
            currentValue[j] = self.tableWidget.item(8,j).text().zfill(5)
        textToSend = self.startMark + ",".join(currentValue) + self.endMark
        self.serial.write(textToSend.encode())
        self.spinBox_M1_1.setValue(int(self.tableWidget.item(8,0).text()))
        self.spinBox_M1_2.setValue(int(self.tableWidget.item(8,1).text()))
        self.spinBox_M1_3.setValue(int(self.tableWidget.item(8,2).text()))
        self.spinBox_M1_4.setValue(int(self.tableWidget.item(8,3).text()))
        self.spinBox_M2_1.setValue(int(self.tableWidget.item(8,4).text()))
        self.spinBox_M2_2.setValue(int(self.tableWidget.item(8,5).text()))
        self.spinBox_M2_3.setValue(int(self.tableWidget.item(8,6).text()))
        self.spinBox_M2_4.setValue(int(self.tableWidget.item(8,7).text()))
        print(textToSend)


    def M1Phase(self):
        self.spinBox_M1_1.setValue(self.MEMSmidValue + self.sliderM1_phase.value() + self.sliderM1_x.value())
        self.spinBox_M1_2.setValue(self.MEMSmidValue + self.sliderM1_phase.value() - self.sliderM1_x.value())
        self.serialDataSend()
        
    def M1x(self):
        self.spinBox_M1_1.setValue(self.MEMSmidValue + self.sliderM1_phase.value() + self.sliderM1_x.value())
        self.spinBox_M1_2.setValue(self.MEMSmidValue + self.sliderM1_phase.value() - self.sliderM1_x.value())
        self.serialDataSend()
    
    def M1y(self):
        self.spinBox_M1_3.setValue(self.MEMSmidValue + self.sliderM1_y.value())
        self.spinBox_M1_4.setValue(self.MEMSmidValue - self.sliderM1_y.value())
        self.serialDataSend()

    def M2Phase(self):
        self.spinBox_M2_1.setValue(self.MEMSmidValue + self.sliderM2_phase.value() + self.sliderM2_x.value())
        self.spinBox_M2_2.setValue(self.MEMSmidValue + self.sliderM2_phase.value() - self.sliderM2_x.value())
        self.serialDataSend()
        
    def M2x(self):
        self.spinBox_M2_1.setValue(self.MEMSmidValue + self.sliderM2_phase.value() + self.sliderM2_x.value())
        self.spinBox_M2_2.setValue(self.MEMSmidValue + self.sliderM2_phase.value() - self.sliderM2_x.value())
        self.serialDataSend()
    
    def M2y(self):
        self.spinBox_M2_3.setValue(self.MEMSmidValue + self.sliderM2_y.value())
        self.spinBox_M2_4.setValue(self.MEMSmidValue - self.sliderM2_y.value())
        self.serialDataSend()
        
    def setP11(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(0,col,item)

    def setP12(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(1,col,item)
            
    def setP13(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(2,col,item)

    def setP21(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(3,col,item)

    def setP22(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(4,col,item)

    def setP23(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(5,col,item)

    def setP31(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(6,col,item)

    def setP32(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(7,col,item)

    def setP33(self):
        data = [self.spinBox_M1_1.value(),self.spinBox_M1_2.value(),self.spinBox_M1_3.value(),self.spinBox_M1_4.value(),self.spinBox_M2_1.value(),self.spinBox_M2_2.value(),self.spinBox_M2_3.value(),self.spinBox_M2_4.value()]
        for col in range(8):
            item = QTableWidgetItem(str(data[col]))
            self.tableWidget.setItem(8,col,item)
            
    def sldDisconnect(self):
        self.sender().valueChanged.disconnect()
        
    def sldReconnectM1_phase(self):
        self.sender().valueChanged.connect(self.M1Phase)
        self.sliderM1_phase.valueChanged['int'].connect(self.spinBox_M1_phase.setValue)
        self.sender().valueChanged.emit(self.sender().value())

    def sldReconnectM1_x(self):
        self.sender().valueChanged.connect(self.M1x)
        self.sliderM1_x.valueChanged['int'].connect(self.spinBox_M1_x.setValue)
        self.sender().valueChanged.emit(self.sender().value())
    
    def sldReconnectM1_y(self):
        self.sender().valueChanged.connect(self.M1y)
        self.sliderM1_y.valueChanged['int'].connect(self.spinBox_M1_y.setValue)
        self.sender().valueChanged.emit(self.sender().value())
        
    def sldReconnectM2_phase(self):
        self.sender().valueChanged.connect(self.M2Phase)
        self.sliderM2_phase.valueChanged['int'].connect(self.spinBox_M2_phase.setValue)
        self.sender().valueChanged.emit(self.sender().value())

    def sldReconnectM2_x(self):
        self.sender().valueChanged.connect(self.M2x)
        self.sliderM2_x.valueChanged['int'].connect(self.spinBox_M2_x.setValue)
        self.sender().valueChanged.emit(self.sender().value())
    
    def sldReconnectM2_y(self):
        self.sender().valueChanged.connect(self.M2y)
        self.sliderM2_y.valueChanged['int'].connect(self.spinBox_M2_y.setValue)
        self.sender().valueChanged.emit(self.sender().value())

    def handleSave(self):
        with open('config.csv', "w", newline='') as fileOutput:
            writer = csv.writer(fileOutput)
            for rowNumber in range(self.tableWidget.rowCount()):          
                fields = [
                    self.tableWidget.item(rowNumber, columnNumber).text() \
                            if self.tableWidget.item(rowNumber, columnNumber) is not None else ""
                    for columnNumber in range(self.tableWidget.columnCount())
                ]                
                writer.writerow(fields)

    def handleOpen(self):
        data = []
        with open('config.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)
                
    def handleOpenG660(self):
        data = []
        with open('configG660.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenG550(self):
        data = []
        with open('configG550.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenG440(self):
        data = []
        with open('configG440.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenG330(self):
        data = []
        with open('configG330.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenB660(self):
        data = []
        with open('configB660.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenB550(self):
        data = []
        with open('configB550.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenB440(self):
        data = []
        with open('configB440.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def handleOpenB330(self):
        data = []
        with open('configB330.csv', 'r') as stream:
            for rowdata in csv.reader(stream):
                data.append(rowdata)
        for row in range (9):
            for col in range(8):
                item = QTableWidgetItem(str(data[row][col]))
                self.tableWidget.setItem(row, col, item)

    def closeProg(self):
        self.serial.close()
        sys.exit(0)
        
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exit(app.exec_())       