import binascii
import struct
import threading
import io
from PIL import Image
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QTimer
from PySide2.QtUiTools import QUiLoader
import serial
import serial.tools.list_ports

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
        self.buffer_size = 440249  # 设置缓冲区大小
        self.received_data = bytes()  # 初始化接收数据的字节串
        # Load the UI file
        self.UI = QUiLoader().load('ui/Receive_UI_Form.ui')
        #接收图片button
        self.UI.pushBtn_receivepicture.clicked.connect(self.start_receive)
        self.timer = QTimer(self) # 创建定时器
        self.timer.timeout.connect(self.update_received_data) # 连接定时器到更新函数

    def start_receive(self):
        if not self.is_receiving:
            # 开始接收数据
            self.is_receiving = True
            self.timer.start(500) # 开始定时器
            self.UI.pushBtn_receivepicture.setText('停止接收')
            self.UI.radioBtn_openser_2.setEnabled(False)
            thread = threading.Thread(target=self.picture_receive, args=())
            thread.setDaemon(True)
            thread.start() # 启动线程
        else:
            # 停止接收数据
            self.is_receiving = False
            self.timer.stop() # 停止定时器
            self.UI.pushBtn_receivepicture.setText('接收图片')
            self.UI.radioBtn_openser_2.setEnabled(True)


    def picture_receive(self):

        print(1)
        while True:

            #a1 = time.time()
            data = self.serial_port.read(self.serial_port.in_waiting or 1)  # 读取串口缓冲区的数据
            if data:  # 判断数据是否为空
                self.received_data += data



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.UI.show()
    app.exec_()
