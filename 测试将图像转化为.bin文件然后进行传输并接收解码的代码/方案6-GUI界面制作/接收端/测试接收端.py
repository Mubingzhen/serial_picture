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
        self.is_receiving = False
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
            self.received_data = bytes()  # 清空接收数据的字节串
            self.timer.stop()

            self.UI.radioBtn_openser_2.setText("打开串口")
            self.UI.pushBtn_sercheck_2.setEnabled(True)
            self.UI.cBox_serselect_2.setEnabled(True)
            self.UI.cBox_Baudrate_2.setEnabled(True)
            self.UI.cBox_bitdate_2.setEnabled(True)
            self.UI.cBOX_checkbit_2.setEnabled(True)
            self.UI.cBOX_stopbit_2.setEnabled(True)
            self.UI.pushBtn_receivepicture.setEnabled(False)
            self.serial_port_is_open = False
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
                #self.serial_port.close()
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



                self.timer.start(500)
                thread = threading.Thread(target=self.picture_receive, args=())
                thread.setDaemon(True)
                thread.start()



            except serial.serialutil.SerialException:
                QtWidgets.QMessageBox.warning(self, "串口已被占用", "此串口已被占用！")
                self.UI.radioBtn_openser_2.setChecked(False)



    def picture_receive(self):
            print(2)
            while True:
                data = self.serial_port.read(self.serial_port.in_waiting or 1)  # 读取串口缓冲区的数据
                if data:  # 判断数据是否为空
                    self.received_data += data
                    if len(self.received_data) >= self.buffer_size:  # 当接收数据的字节串长度达到缓冲区大小时
                        with open('received_output.bin', 'ab') as f:  # 以二进制追加模式打开文件
                            f.write(self.received_data)  # 将接收数据写入文件
                        self.received_data = bytes()  # 清空接收数据的字节串
                        with open('received_output.bin', 'rb') as f:
                            b_io = io.BytesIO(f.read())
                            # 读取二进制文件的宽度和高度
                            width, height = struct.unpack('2i', b_io.read(8))
                            # 创建一个新的RGB图像对象
                            img = Image.new('RGB', (width, height))
                            # 循环遍历二进制文件中的每个像素，并将其设置为图像的RGB值
                            for y in range(height):
                                for x in range(width):
                                    r, g, b = struct.unpack('BBB', b_io.read(3))
                                    img.putpixel((x, y), (r, g, b))
                            # 保存还原的图像
                            img.save('方案6_restored_image.jpg')
                            # Load the image and scale it to 569x572
                            image = QtGui.QPixmap('方案6_restored_image.jpg').scaled(569, 572, aspectRatioMode=QtCore.Qt.KeepAspectRatio)
                            # Set the pixmap of the QLabel
                            self.UI.label_graphics_2.setPixmap(image)
                            # Set the size and position of the QLabel
                            self.UI.label_graphics_2.setGeometry(QtCore.QRect(352, 42, 569, 562))
                            # 关闭串口
                            self.serial_port.close()
                            self.serial_port = None  # 将串口对象设为 None
                            break
    def update_received_data(self):
        print(2)
        hex_str = binascii.hexlify(
            self.received_data.replace(b'\r', b'').replace(b'\n', b'').replace(b'\x00', b'')).decode()
        spaced_hex_str = ' '.join([hex_str[i:i + 2] for i in range(0, len(hex_str), 2)])
        self.UI.textBrowser_showreceivedata_2.setText(spaced_hex_str)
        scroll_bar = self.UI.textBrowser_showreceivedata_2.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def receiveclear(self):
        self.UI.textBrowser_showreceivedata_2.clear()
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.UI.show()
    app.exec_()
