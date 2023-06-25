from PIL import Image
import struct
import os
import serial
import struct
import time

# 打开彩色图像
img = Image.open('2.jpg')

# 转换为RGB格式
img = img.convert('RGB')

# 获取图像的宽度和高度
width, height = img.size

# 计算需要传输的数据包数量
num_packets = (width * height * 3 + 150 - 1) // 150
print(f'num_packets={num_packets}')
# 创建二进制文件并写入宽度和高度的值
with open('方案5_output.bin', 'wb') as f:
    f.write(struct.pack('2i', width, height))

    # 循环遍历图像的每个像素，并将RGB值写入二进制文件
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            f.write(struct.pack('BBB', r, g, b))
file_size = os.path.getsize('方案5_output.bin')
print(f'file_size={file_size}')
last_packet_size = file_size % 150
print(f'last_packet_size={last_packet_size}')

#print(type(last_packet_size))

# 创建串口连接
serial_port = serial.Serial('COM1', 115200, timeout=0.5)
'''
# 发送要传输的数据包数量给接收端
file_size_data = struct.pack('i', file_size)
if len(file_size_data) < 300:
    file_size_data += b'\x00' * (300 - len(file_size_data))
ser.write(file_size_data)
#ser.write(struct.pack('ii', num_packets,last_packet_size))
'''
'''
# 等待接收端回复A
while True:
    if ser.in_waiting > 0:
        response = ser.read().decode('ascii')
        if response == 'A':
            break
while True:
    if ser.in_waiting > 0:
        response = ser.read().decode('ascii')
        if response == 'A':
            break
# 计算需要传输的数据包数量和最后一个数据包的字节数
num_packets = (width * height * 3 + 150 - 1) // 150
'''
# 打开二进制文件，创建缓冲区
with open('方案5_output.bin', 'rb') as f:
    # 循环发送数据
    for i in range(num_packets):
        if i == 0:

            data = f.read(300)
            serial_port.write(data)
            sendbits = 0

            while True:
                if serial_port.in_waiting > 0:
                    response = serial_port.read().decode('ascii')
                    if response == 'A':
                        break
        # 读取150位数据
        if i < num_packets - 1:

            data = f.read(150)

            serial_port.write(data)

            # time.sleep(0.0001)
            # 等待接收端回复
            while True:
                if serial_port.in_waiting > 0:
                    response = serial_port.read().decode('ascii')
                    if response == 'A':
                        break
        if i == num_packets - 1 and last_packet_size > 0:
            # 处理最后一个数据包不足240字节的情况
            data = f.read(last_packet_size)
            sendbits += last_packet_size
            serial_port.write(data)

serial_port.close()
print("发送完毕！")
print("传输结束，关闭串口连接！")