def init(self):
    # 串口检测按钮button
    self.pushBtn_sercheck.clicked.connect(self.port_check)

    '''
    # 串口选择信息显示
    self.cBox_serselect.currentTextChanged.connect(self.port_information)'''

    # 打开串口按钮butoon
    self.radioBtn_openser.clicked.connect(self.openser)

    # 定时发送数据buttton
    self.timer_send = QTimer()
    self.timer_send.timeout.connect(self.data_send)
    self.radioBtn_timedsend.stateChanged.connect(self.data_send_timer)

    '''
    # 定时器接收数据
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.data_receive)'''

    # 发送button
    self.pushBtn_send.clicked.connect(self.data_send)

    # 清除发送窗口button
    self.pushBtn_clear.clicked.connect(self.send_data_byuself_clear)

    # 清除接收窗口button
    self.pushBtn_clear_2.clicked.connect(self.send_data_clear)

    # 选择图片button
    self.pushBtn_selectpicture.clicked.connect(self.selectpicture)
    # 发送图片button
    self.pushBtn_sendpicture.clicked.connect(self.sendpicture)

    # 串口检测


def port_check(self):
    # 检测所有存在的串口，将信息存储在字典中
    self.Com_Dict = {}
    port_list = list(serial.tools.list_ports.comports())
    self.cBox_serselect.clear()
    for port in port_list:
        self.Com_Dict["%s" % port[0]] = "%s" % port[1]
        self.cBox_serselect.addItem(port[0])
    if len(self.Com_Dict) == 0:
        self.state_label.setText(" 无串口")

    # 串口信息


def port_information(self):
    # 显示选定的串口的详细信息
    information = self.cBox_serselect.currentText()
    if information != "":
        self.state_label.setText(self.Com_Dict[self.cBox_serselect.currentText()])

    # 打开串口


def openser(self):
    if self.radioBtn_openser.isChecked():
        self.ser.port = self.cBox_serselect.currentText()
        self.ser.baudrate = int(self.cBox_Baudrate.currentText())
        self.ser.bytesize = int(self.cBox_bitdate.currentText())
        self.ser.stopbits = int(self.cBOX_stopbit.currentText())
        self.ser.parity = self.cBOX_checkbit.currentText()
        try:
            self.ser.open()
        except:
            QMessageBox.critical(self, "Port Error", "此串口不能被打开！")
            return None
    else:
        self.timer.stop()
        self.timer_send.stop()
        try:
            self.ser.close()
        except:
            pass
        self.data_num_sended = 0
        self.lineEdit_sent.setText(str(self.data_num_sended))

    # 发送数据


def data_send(self):
    if self.ser.isOpen():
        input_s = self.textBrowser_byuselfsend.toPlainText()
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
            self.lineEdit_sent.setText(str(self.data_num_sended))
    else:
        pass

    # 定时发送数据


def data_send_timer(self):
    if self.radioBtn_timedsend.isChecked():
        self.timer_send.start(int(self.lineEdit_sendinterval.text()))
        self.lineEdit_sendinterval.setEnabled(False)
    else:
        self.timer_send.stop()
        self.lineEdit_sendinterval.setEnabled(True)

    # 清除显示


def send_data_clear(self):
    self.textBrowser_showsenddate.setText("")


def send_data_byuself_clear(self):
    self.textBrowser_byuselfsend.setText("")


def selectpicture(self):
    # 打开文件对话框，选择图片文件
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.gif")])
    if file_path:
        # 通过PIL库中的Image打开选择的图片文件
        img = Image.open(file_path)
        # 转换为RGB格式
        img = img.convert('RGB')

        # 获取图像的宽度和高度
        width, height = img.size

        # 计算需要传输的数据包数量
        num_packets = ((width * height * 3 + 150 - 1) // 150) - 1
        # 创建二进制文件并写入宽度和高度的值
        with open('方案5_output.bin', 'wb') as f:
            f.write(struct.pack('2i', width, height))

            # 循环遍历图像的每个像素，并将RGB值写入二进制文件
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    f.write(struct.pack('BBB', r, g, b))
        file_size = os.path.getsize('方案5_output.bin')
        last_packet_size = file_size % 150


def sendpicture(self, num_packets=None, last_packet_size=None):
    with open('方案5_output.bin', 'rb') as f:
        # 循环发送数据
        for i in range(num_packets):
            if i == 0:
                data = f.read(300)
                self.ser.write(data)
                while True:
                    if self.ser.in_waiting > 0:
                        response = self.ser.read().decode('ascii')
                        if response == 'A':
                            break
            # 读取150位数据
            if i < num_packets - 1:
                data = f.read(150)
                # 计算校验和并添加到数据末尾
                # 发送数据
                self.ser.write(data)
                # time.sleep(0.0001)
                # 等待接收端回复
                while True:
                    if self.ser.in_waiting > 0:
                        response = self.ser.read().decode('ascii')
                        if response == 'A':
                            break
            if i == num_packets - 1 and last_packet_size > 0:
                # 处理最后一个数据包不足240字节的情况
                data = f.read(last_packet_size)
                # 填充为240个字节
                # data += b'\x00' * (240 - last_packet_size)
                self.ser.write(data)
