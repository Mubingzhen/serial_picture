import sys
import serial
import os
import serial.tools.list_ports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox,QFileDialog
from PyQt5.QtCore import QTimer
from ui_test import Ui_Form
import struct
from PIL import Image

class Pyqt5_Serial(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super(Pyqt5_Serial, self).__init__()
        self.setupUi(self)
        self.init()
        self.setWindowTitle("串口调试助手")
        self.ser = serial.Serial()
        self.port_check()

        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))



    def init(self):
        # 串口检测按钮
        self.s1__box_1.clicked.connect(self.port_check)

        # 串口信息显示
        self.s1__box_2.currentTextChanged.connect(self.port_imf)

        # 打开串口按钮
        self.open_button.clicked.connect(self.port_open)

        # 关闭串口按钮
        self.close_button.clicked.connect(self.port_close)

        # 发送数据按钮
        self.s3__send_button.clicked.connect(self.data_send)

        # 定时发送数据
        self.timer_send = QTimer()
        self.timer_send.timeout.connect(self.data_send)
        self.timer_send_cb.stateChanged.connect(self.data_send_timer)

        # 定时器接收数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.data_receive)

        # 清除发送窗口
        self.s3__clear_button.clicked.connect(self.send_data_clear)

        # 清除接收窗口
        self.s2__clear_button.clicked.connect(self.receive_data_clear)

        #选择文件按钮
        self.choosefile_buttton.clicked.connect(self.selectFile)

        #发送文件按钮
        self.sendfile_button.clicked.connect(self.sendFile)

    # 串口检测
    def port_check(self):
        # 检测所有存在的串口，将信息存储在字典中
        self.Com_Dict = {}
        port_list = list(serial.tools.list_ports.comports())
        self.s1__box_2.clear()
        for port in port_list:
            self.Com_Dict["%s" % port[0]] = "%s" % port[1]
            self.s1__box_2.addItem(port[0])
        if len(self.Com_Dict) == 0:
            self.state_label.setText(" 无串口")

    # 串口信息
    def port_imf(self):
        # 显示选定的串口的详细信息
        imf_s = self.s1__box_2.currentText()
        if imf_s != "":
            self.state_label.setText(self.Com_Dict[self.s1__box_2.currentText()])

    # 打开串口
    def port_open(self):
        self.ser.port = self.s1__box_2.currentText()
        self.ser.baudrate = int(self.s1__box_3.currentText())
        self.ser.bytesize = int(self.s1__box_4.currentText())
        self.ser.stopbits = int(self.s1__box_6.currentText())
        self.ser.parity = self.s1__box_5.currentText()

        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None

        # 打开串口接收定时器，周期为2ms
        self.timer.start(2)

        if self.ser.isOpen():
            self.open_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.formGroupBox1.setTitle("串口状态（已开启）")

    # 关闭串口
    def port_close(self):
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.open_button.setEnabled(True)
        self.close_button.setEnabled(False)
        self.lineEdit_3.setEnabled(True)
        # 接收数据和发送数据数目置零
        self.data_num_received = 0
        self.lineEdit.setText(str(self.data_num_received))
        self.data_num_sended = 0
        self.lineEdit_2.setText(str(self.data_num_sended))
        self.formGroupBox1.setTitle("串口状态（已关闭）")

    # 发送数据
    def data_send(self):
        if self.ser.isOpen():
            input_s = self.s3__send_text.toPlainText()
            if input_s != "":
                # 非空字符串
                if self.hex_send.isChecked():
                    # hex发送
                    input_s = input_s.strip()
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)
                        except ValueError:
                            QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                            return None
                        input_s = input_s[2:].strip()
                        send_list.append(num)
                    input_s = bytes(send_list)
                else:
                    # ascii发送
                    input_s = (input_s + '\r\n').encode('utf-8')

                num = self.ser.write(input_s)
                self.data_num_sended += num
                self.lineEdit_2.setText(str(self.data_num_sended))
        else:
            pass

    # 接收数据
    def data_receive(self):
        try:
            num = self.ser.inWaiting()
        except:
            self.port_close()
            return None
        if num > 0:
            data = self.ser.read(num)
            num = len(data)
            # hex显示
            if self.hex_receive.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '
                self.s2__receive_text.insertPlainText(out_s)
            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.s2__receive_text.insertPlainText(data.decode('utf-8'))

            # 统计接收字符的数量
            self.data_num_received += num
            self.lineEdit.setText(str(self.data_num_received))

            # 获取到text光标
            textCursor = self.s2__receive_text.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.s2__receive_text.setTextCursor(textCursor)
        else:
            pass

    # 定时发送数据
    def data_send_timer(self):
        if self.timer_send_cb.isChecked():
            self.timer_send.start(int(self.lineEdit_3.text()))
            self.lineEdit_3.setEnabled(False)
        else:
            self.timer_send.stop()
            self.lineEdit_3.setEnabled(True)

    # 清除显示
    def send_data_clear(self):
        self.s3__send_text.setText("")

    def receive_data_clear(self):
        self.s2__receive_text.setText("")

    #选择文件
    def selectFile(self):
        # 打开文件对话框
      #  fileName, _ = QFileDialog.getOpenFileName(self, '选择文件', os.getcwd())
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "选择文件", os.getcwd(),
                                                                   "All Files(*);;Text Files(*.txt)")
        if fileName:
            self.receive_file_2.setText('已选择文件: {}'.format(fileName))
        else:
            self.receive_file_2.setText('未选择文件')
    #发送文件
    def sendFile(self):
        img = Image.open('1.jpg')

        # 转换为RGB格式
        img = img.convert('RGB')

        # 获取图像的宽度和高度
        width, height = img.size

        # 计算需要传输的数据包数量
        num_packets = (width * height * 3 + 240 - 1) // 240
        print(num_packets)
        # 创建二进制文件并写入宽度和高度的值
        with open('方案3_output.bin', 'wb') as f:
            f.write(struct.pack('2i', width, height))

            # 循环遍历图像的每个像素，并将RGB值写入二进制文件
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    f.write(struct.pack('BBB', r, g, b))
        file_size = os.path.getsize('方案3_output.bin')
        print(file_size)
        last_packet_size = file_size % 240
        print(last_packet_size)

        print(type(last_packet_size))
        # 创建串口连接
        ser = serial.Serial('COM1', 115200, timeout=0.5)

        # 发送要传输的数据包数量给接收端
        packed_data = struct.pack('ii', num_packets, last_packet_size)
        ser.write(packed_data)
        # ser.write(struct.pack('ii', num_packets,last_packet_size))

        # 等待接收端回复A
        while True:
            if ser.in_waiting > 0:
                response = ser.read().decode('ascii')
                if response == 'A':
                    break
        # 计算需要传输的数据包数量和最后一个数据包的字节数
        num_packets = (width * height * 3 + 240 - 1) // 240

        # 打开二进制文件，创建缓冲区
        with open('方案3_output.bin', 'rb') as f:
            # 循环发送数据
            for i in range(num_packets):
                # 读取240位数据
                if i < num_packets - 1:

                    data = f.read(240)
                    # 计算校验和并添加到数据末尾
                    checksum = sum(data) & 0xFF
                    senddata = data + struct.pack('B', checksum)

                    # 发送数据
                    ser.write(senddata)
                    # 等待接收端回复
                    while True:
                        if ser.in_waiting > 0:
                            response = ser.read().decode('ascii')
                            if response == 'B':
                                break
                            elif response == 'C':
                                # 发送端得重新发送这240位数据
                                ser.write(senddata)

                                # 等待接收端回复
                                while True:
                                    if ser.in_waiting > 0:
                                        response = ser.read().decode('ascii')
                                        if response == 'B':
                                            break
                                        elif response == 'C':
                                            ser.write(senddata)
                                            break
                                continue
                            elif response == 'D':
                                ser.close()
                                print("发送完毕，关闭串口连接！")
                if i == num_packets - 1 and last_packet_size > 0:
                    # 处理最后一个数据包不足240字节的情况
                    data = f.read(last_packet_size)
                    # 填充为240个字节
                    # data += b'\x00' * (240 - last_packet_size)
                    checksum = sum(data) & 0xFF
                    senddata = data + struct.pack('B', checksum)
                    ser.write(senddata)
                    while True:
                        if ser.in_waiting > 0:
                            response = ser.read().decode('ascii')
                            if response == 'B':

                                break
                            elif response == 'C':
                                # 发送端得重新发送这240位数据
                                ser.write(senddata)
                            if response == 'D':
                                break
        ser.close()
        print("发送完毕！")
        print("传输结束，关闭串口连接！")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myshow = Pyqt5_Serial()
    myshow.show()
    sys.exit(app.exec_())