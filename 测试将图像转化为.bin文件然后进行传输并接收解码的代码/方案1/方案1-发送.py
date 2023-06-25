import os.path

import serial
import time

ser = serial.Serial('COM1', 115200)  # 串口初始化，需要根据实际情况修改端口和波特率

with open('2.jpg', 'rb') as f:
    data = f.read()
file_size=os.path.getsize('2.jpg')
print(file_size)
last_packet_size=file_size%150
print(last_packet_size)
num_packets=file_size//150
print(num_packets)
while True:
    for i in range(0, len(data), 300):  # 将数据分块，每块64字节
        block = data[i:i+300]
        ser.write(block)  # 发送数据块
        #time.sleep(0.01)  # 等待一段时间，避免数据发送过快
    ser.close()
print("发送成功！")