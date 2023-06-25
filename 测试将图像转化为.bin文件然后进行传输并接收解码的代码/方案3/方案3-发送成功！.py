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
#ser.write(struct.pack('ii', num_packets,last_packet_size))

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
            #data += b'\x00' * (240 - last_packet_size)
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
                    if response=='D':
                        break
ser.close()
print("发送完毕！")
print("传输结束，关闭串口连接！")