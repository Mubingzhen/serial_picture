import serial
import serial
import struct
import os
import time
from PIL import Image
import io

ser = serial.Serial('COM5', 115200)  # 根据实际情况设置串口参数
buffer_size = 440249  # 设置缓冲区大小
received_data = bytes()  # 初始化接收数据的字节串

while True:
    a1=time.time()
    data = ser.read(ser.in_waiting or 1)  # 读取串口缓冲区的数据
    if data:  # 判断数据是否为空
        received_data += data  # 将读取到的数据添加到接收数据的字节串中
        if len(received_data) >= buffer_size:  # 当接收数据的字节串长度达到缓冲区大小时
            with open('received_output.bin', 'ab') as f:  # 以二进制追加模式打开文件
                f.write(received_data)  # 将接收数据写入文件
            received_data = bytes()  # 清空接收数据的字节串
            with open('received_output.bin','rb') as f:
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
                img.save('方案5_restored_image.jpg')
                a2 = time.time()
                print(a2 - a1)
                break
ser.close()  # 关闭串口
