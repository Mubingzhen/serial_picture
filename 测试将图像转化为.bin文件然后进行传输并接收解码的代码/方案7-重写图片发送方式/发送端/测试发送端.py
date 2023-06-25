import math
import os
import struct
from tkinter import filedialog

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtUiTools import QUiLoader
import serial
import serial.tools.list_ports
import time


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # 创建串口对象并设置默认值
        self.serial_port = None
        self.serial_port_is_open = False
        self.default_baudrate = 9600
        self.default_bytesize = 8
        self.default_parity = 'N'
        self.default_stopbits = 1
        self.num_packets=0
        self.last_packet_size=0
        self.sendbits=0
        # Load the UI file
        self.UI = QUiLoader().load('ui/Send_UI_Form.ui')



        print(self.sendbits)
        #初始化
        self.UI.pushBtn_sercheck.setEnabled(True)
        self.UI.cBox_serselect.setEnabled(True)
        self.UI.cBox_Baudrate.setEnabled(True)
        self.UI.cBox_bitdate.setEnabled(True)
        self.UI.cBOX_checkbit.setEnabled(True)
        self.UI.cBOX_stopbit.setEnabled(True)
        self.UI.pushBtn_selectpicture.setEnabled(False)
        self.UI.pushBtn_sendpicture.setEnabled(False)

        self.port_check()
       #串口检测button
        self.UI.pushBtn_sercheck.clicked.connect(self.port_check)
        # 打开串口按钮butoon
        self.UI.radioBtn_openser.clicked.connect(self.openser)
        #选择图片button
        self.UI.pushBtn_selectpicture.clicked.connect(self.select_picture)
        #发送图片button
        self.UI.pushBtn_sendpicture.clicked.connect(self.send_picture)
        #清除发送区
        self.UI.pushBtn_sendclear.clicked.connect(self.sendclear)
        #清除接收区
        self.UI.pushBtn_receiveclear.clicked.connect(self.receiveclear)

        #self.UI.label_sendshow.setText("新的文本")
    # 串口检测
    def port_check(self):
        self.UI.cBox_serselect.clear()
        # 检测所有存在的串口，将信息存储在字典中
        # 获取所有可用串口
        ports = list(serial.tools.list_ports.comports())
        #print(ports)
        # 在QComboBox中添加串口列表
        for port in ports:
            self.UI.cBox_serselect.addItem(str(port.device))

    # 打开串口
    def openser(self):


        if self.serial_port_is_open:
            # 关闭串口
            self.serial_port.close()
            self.serial_port_is_open = False
            self.UI.radioBtn_openser.setText("打开串口")
            self.UI.pushBtn_sercheck.setEnabled(True)
            self.UI.cBox_serselect.setEnabled(True)
            self.UI.cBox_Baudrate.setEnabled(True)
            self.UI.cBox_bitdate.setEnabled(True)
            self.UI.cBOX_checkbit.setEnabled(True)
            self.UI.cBOX_stopbit.setEnabled(True)
            self.UI.pushBtn_selectpicture.setEnabled(False)
            self.UI.pushBtn_sendpicture.setEnabled(False)
        else:
            # 获取所有可用串口
            port = str(self.UI.cBox_serselect.currentText())


            # 获取波特率、数据位、校验位和停止位
            baudrate = int(self.UI.cBox_Baudrate.currentText())
            bytesize = int(self.UI.cBox_bitdate.currentText())
            # 设置校验位
            parity_index = self.UI.cBOX_checkbit.currentIndex()
            if parity_index == 0:
                parity = serial.PARITY_NONE
            elif parity_index == 1:
                parity = serial.PARITY_ODD
            elif parity_index == 2:
                parity = serial.PARITY_EVEN
            else:
                parity = serial.PARITY_NONE  # 默认值为无校验
            stopbits = float(self.UI.cBOX_stopbit.currentText())

            # 创建串口对象并打开串口
            try:
                self.serial_port = serial.Serial(port, baudrate, bytesize, parity, stopbits)
                print(self.serial_port)

                self.serial_port_is_open = True
                self.UI.radioBtn_openser.setText("关闭串口")

                self.UI.pushBtn_sercheck.setEnabled(False)
                self.UI.cBox_serselect.setEnabled(False)
                self.UI.cBox_Baudrate.setEnabled(False)
                self.UI.cBox_bitdate.setEnabled(False)
                self.UI.cBOX_checkbit.setEnabled(False)
                self.UI.cBOX_stopbit.setEnabled(False)
                self.UI.pushBtn_selectpicture.setEnabled(True)
                self.UI.pushBtn_sendpicture.setEnabled(False)

            except serial.serialutil.SerialException:
                QtWidgets.QMessageBox.warning(self, "串口已被占用", "此串口已被占用！")
                self.UI.radioBtn_openser.setChecked(False)
    def select_picture(self):
        if self.serial_port_is_open == True:
            self.file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a picture', '',
                                                                 'Images (*.png *.xpm *.jpg *.bmp *.gif)')
            if self.file_path:
                # Load the image and scale it to 569x572
                image = QtGui.QPixmap(self.file_path).scaled(569, 572, aspectRatioMode=QtCore.Qt.KeepAspectRatio)
                # Set the pixmap of the QLabel
                self.UI.label_graphics.setPixmap(image)
                # Set the size and position of the QLabel
                self.UI.label_graphics.setGeometry(QtCore.QRect(352, 42, 569, 562))
                # 打开彩色图像
                #img = Image.open(self.file_path)
                self.file_size=os.path.getsize(self.file_path)
                print(f'图片大小={self.file_size}')
                self.num_packets=math.ceil(self.file_size/150)
                print(f'发送次数={self.num_packets}')
                self.last_packet_size=self.file_size%150
                print(f'最后一包={self.last_packet_size}')
                self.UI.pushBtn_sendpicture.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(self, '警告！', '请先打开串口！')

    def send_picture(self):
        if self.UI.label_graphics.pixmap() is None:
            QtWidgets.QMessageBox.warning(self, '警告！', '请先选择一张图片！')
        else:
            size_byets = struct.pack('>H',self.file_size)
            time.sleep(1)
            # 打开二进制文件，创建缓冲区
            with open(self.file_path, 'rb') as f:
                self.serial_port.write(size_byets)
                # 循环发送数据
                for i in range(self.num_packets):
                    if i == 0:

                        data = f.read(300)
                        self.serial_port.write(data)
                        self.sendbits=150

                        self.UI.label_sendshow.setText(str(300))
                        self.UI.label_sendshow.repaint()
                        # 将数据转换为16进制字符串
                        hex_data = ' '.join(format(byte, '02x') for byte in data)

                        # 在textBrowser_showsenddata中显示16进制字符串
                        self.UI.textBrowser_showsenddata.append(hex_data.upper())
                        # 刷新界面
                        self.UI.textBrowser_showsenddata.repaint()

                    # 读取150位数据
                    if i < self.num_packets - 1 and i!=0:

                        data = f.read(150)
                        self.sendbits+=150
                        self.UI.label_sendshow.setText(str(self.sendbits))
                        self.UI.label_sendshow.repaint()
                        # 将数据转换为16进制字符串
                        hex_data = ' '.join(format(byte, '02x') for byte in data)

                        # 在textBrowser_showsenddata中显示16进制字符串
                        self.UI.textBrowser_showsenddata.append(hex_data.upper())
                        # 刷新界面
                        self.UI.textBrowser_showsenddata.repaint()


                        # 计算校验和并添加到数据末尾
                        # 发送数据
                        self.serial_port.write(data)

                        # time.sleep(0.0001)

                    if i == self.num_packets - 1 and self.last_packet_size > 0:

                        # 处理最后一个数据包不足240字节的情况
                        data = f.read(self.last_packet_size)
                        self.sendbits+=self.last_packet_size


                        # 将数据转换为16进制字符串
                        hex_data = ' '.join(format(byte, '02x') for byte in data)

                        # 在textBrowser_showsenddata中显示16进制字符串
                        self.UI.textBrowser_showsenddata.append(hex_data.upper())
                        # 刷新界面
                        self.UI.textBrowser_showsenddata.repaint()


                        print(self.sendbits)
                        # 填充为240个字节
                        # data += b'\x00' * (240 - last_packet_size)
                        self.serial_port.write(data)
                        self.UI.textBrowser_showsenddata.append(hex_data.upper())


                        self.UI.label_sendshow.setText(str(self.sendbits))

                        QtWidgets.QMessageBox.warning(self, '通知', '发送成功！')



    def sendclear(self):
        self.UI.textBrowser_showsenddata.clear()
    def receiveclear(self):
        self.UI.textBrowser_showreceivedata.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.UI.show()
    app.exec_()
