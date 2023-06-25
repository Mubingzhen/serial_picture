import serial
import struct
import os
import time
from PIL import Image
import io

# 创建串口连接
ser = serial.Serial('COM2', 115200, timeout=None)

# 等待发送端发送数据包数量和最后一个数据包的大小
while True:
    data1=ser.read(8)
    num_packets1,last_packet_size1 = struct.unpack('ii', data1)
    print(num_packets1,last_packet_size1)
    ser.write(b'A')
    break

# 创建二进制文件并写入宽度和高度的值
with open('received_output.bin', 'wb') as f:
    # 循环接收数据包
    for i in range(num_packets1):
        if i < num_packets1 - 1 :

            # 等待发送端发送数据包
            while True:
                if ser.in_waiting >= 241:
                    data = ser.read(241)
                    break

            # 解析数据包
            checksum = sum(data[:240]) & 0xff
            if checksum == data[240]:
                f.write(data[:240])
                ser.write(b'B')
                start_time = time.time()
                resend_count = 0  # 初始化重发计数器
                while ser.in_waiting == 0:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0.5:
                        if resend_count < 3:  # 如果重发次数小于3，则重新发送B
                            ser.write(b'B')
                            start_time = time.time()
                            resend_count += 1
                        else:  # 如果重发次数超过3，则放弃
                            print("重发B超过3次，放弃本数据包！")
                            break
            else:
                ser.write(b'C')
        if i == num_packets1 - 1 and last_packet_size1 > 0:
            # 处理最后一个数据包不足240字节的情况
            while True:
                if ser.in_waiting >= last_packet_size1 + 1:
                    # 读取数据并计算校验和
                    data = ser.read(last_packet_size1)
                    checksum = sum(data) & 0xFF

                    # 读取校验和并进行验证
                    received_checksum = ser.read(1)[0]
                    if received_checksum == checksum:
                        # 写入数据并发送确认
                        f.write(data)
                        ser.write(b'B')
                        print("接收到最后一个数据包并发送确认！")
                    else:
                        # 发送重新请求并继续循环
                        ser.write(b'C')
                        print("接收到最后一个数据包但校验和错误，重新请求数据！")
                    break



            '''while True:
                if ser.in_waiting >= 241:
                    data = ser.read(last_packet_size1)
                    break
                f.write(data[:last_packet_size1])
                ser.write(b'D')
                break'''

ser.close()
print("传输结束，关闭串口连接！")
with open('方案3_output.bin', 'rb') as f:
    #ser = f.read()
    b_io= io.BytesIO(f.read())

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
img.save('方案3_restored_image.jpg')