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
        self.buffer_size = 1113505  # 设置缓冲区大小
        self.received_data = io.BytesIO()  # 初始化接收数据的字节串
        self.is_receiving = False
        self.buffer=io.BytesIO()
        self.data_length = 0
        # Load the UI file
        self.UI = QUiLoader().load('ui/Receive_UI_Form.ui')
        self.exit_flag=False

        #初始化
        self.UI.pushBtn_sercheck_2.setEnabled(True)
        self.UI.cBox_serselect_2.setEnabled(True)
        self.UI.cBox_Baudrate_2.setEnabled(True)
        self.UI.cBox_bitdate_2.setEnabled(True)
        self.UI.cBOX_checkbit_2.setEnabled(True)
        self.UI.cBOX_stopbit_2.setEnabled(True)
        self.UI.pushBtn_receivepicture.setEnabled(False)

        self.port_check()
        #串口检测button
        self.UI.pushBtn_sercheck_2.clicked.connect(self.port_check)
        # 打开串口按钮butoon
        self.UI.radioBtn_openser_2.clicked.connect(self.openser)
        #接收图片button
        self.UI.pushBtn_receivepicture.clicked.connect(self.start_receive)
        #清除接收区
        self.UI.pushBtn_receiveclear_2.clicked.connect(self.receiveclear)

        self.timer = QTimer(self) # 创建定时器
        self.timer.timeout.connect(self.update_received_data) # 连接定时器到更新函数
    # 串口检测
    def port_check(self):
        self.UI.cBox_serselect_2.clear()
        # 检测所有存在的串口，将信息存储在字典中
        # 获取所有可用串口
        ports = list(serial.tools.list_ports.comports())
        #print(ports)
        # 在QComboBox中添加串口列表
        for port in ports:
            self.UI.cBox_serselect_2.addItem(str(port.device))

    # 打开串口
    def openser(self):


        if self.serial_port_is_open:
            # 关闭串口
            self.exit_flag = True
            self.serial_port.close()
            self.serial_port_is_open = False
            self.UI.radioBtn_openser_2.setText("打开串口")
            self.UI.pushBtn_sercheck_2.setEnabled(True)
            self.UI.cBox_serselect_2.setEnabled(True)
            self.UI.cBox_Baudrate_2.setEnabled(True)
            self.UI.cBox_bitdate_2.setEnabled(True)
            self.UI.cBOX_checkbit_2.setEnabled(True)
            self.UI.cBOX_stopbit_2.setEnabled(True)
            self.UI.pushBtn_receivepicture.setEnabled(False)
        else:
            # 获取所有可用串口
            port = str(self.UI.cBox_serselect_2.currentText())

            # 获取波特率、数据位、校验位和停止位
            baudrate = int(self.UI.cBox_Baudrate_2.currentText())
            bytesize = int(self.UI.cBox_bitdate_2.currentText())
            # 设置校验位
            parity_index = self.UI.cBOX_checkbit_2.currentIndex()
            if parity_index == 0:
                parity = serial.PARITY_NONE
            elif parity_index == 1:
                parity = serial.PARITY_ODD
            elif parity_index == 2:
                parity = serial.PARITY_EVEN
            else:
                parity = serial.PARITY_NONE  # 默认值为无校验
            stopbits = float(self.UI.cBOX_stopbit_2.currentText())
            try:
            # 创建串口对象并打开串口
                self.serial_port = serial.Serial(port, baudrate, bytesize, parity, stopbits)
                print(self.serial_port)
                #self.serial_port.open()

                self.serial_port_is_open = True
                self.UI.radioBtn_openser_2.setText("关闭串口")

                self.UI.pushBtn_sercheck_2.setEnabled(False)
                self.UI.cBox_serselect_2.setEnabled(False)
                self.UI.cBox_Baudrate_2.setEnabled(False)
                self.UI.cBox_bitdate_2.setEnabled(False)
                self.UI.cBOX_checkbit_2.setEnabled(False)
                self.UI.cBOX_stopbit_2.setEnabled(False)
                self.UI.pushBtn_receivepicture.setEnabled(True)
                # 清空串口输入缓冲区
                self.serial_port.reset_input_buffer()
            except serial.serialutil.SerialException:
                QtWidgets.QMessageBox.warning(self, "串口已被占用", "此串口已被占用！")
                self.UI.radioBtn_openser_2.setChecked(False)

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
            self.exit_flag=False
        else:
            # 停止接收数据
            self.is_receiving = False
            self.timer.stop() # 停止定时器
            self.UI.pushBtn_receivepicture.setText('接收图片')
            self.exit_flag = True

            self.UI.radioBtn_openser_2.setEnabled(True)
    def picture_receive(self):
            print(1)
            while True:
                if self.exit_flag == False:

                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)  # 读取串口接收到的所有数据
                        self.buffer.write(data)  # 将数据写入缓存
                        byte_data = self.buffer.getvalue()
                        self.data_length = len(byte_data)
                        print(self.data_length)

                        print(self.buffer.getvalue())

                    if self.buffer.tell() >= 1113505:  # 如果接收到的数据长度达到图片的长度
                        self.buffer.seek(0)  # 将缓存指针移到起始位置
                        img_data = self.buffer.read()  # 读取缓存中的数据
                        img = Image.open(io.BytesIO(img_data))  # 用PIL库打开图像
                        img.save("666.jpg")
                        self.received_data=self.buffer
                        self.buffer = io.BytesIO()  # 清空缓存
                        print("接收完毕")
                        # Load the image and scale it to 569x572
                        image = QtGui.QPixmap('666.jpg').scaled(569, 572, aspectRatioMode=QtCore.Qt.KeepAspectRatio)
                        # Set the pixmap of the QLabel
                        self.UI.label_graphics_2.setPixmap(image)
                        # Set the size and position of the QLabel
                        self.UI.label_graphics_2.setGeometry(QtCore.QRect(352, 42, 569, 562))

                else:
                    break
    def update_received_data(self):
        print(2)
        hex_str = binascii.hexlify(self.received_data.getvalue()).decode()
        self.UI.label_receiveshow.setText(str(self.data_length))
        self.UI.label_receiveshow.repaint()
        spaced_hex_str = ' '.join([hex_str[i:i + 2].upper() for i in range(0, len(hex_str), 2)])
        self.UI.textBrowser_showreceivedata_2.setText(spaced_hex_str)
        scroll_bar = self.UI.textBrowser_showreceivedata_2.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def receiveclear(self):
        self.UI.textBrowser_showreceivedata_2.clear()
        self.received_data=io.BytesIO()
        self.buffer = io.BytesIO()  # 清空缓存
        self.data_length=0
        self.UI.label_graphics_2.clear()  # 清除图片显示区域的内容
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.UI.show()
    app.exec_()
