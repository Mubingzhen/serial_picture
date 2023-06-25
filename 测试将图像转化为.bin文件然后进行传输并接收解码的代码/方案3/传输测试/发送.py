import struct
import serial
a=1835
b=89


# 创建串口连接
ser = serial.Serial('COM1', 115200, timeout=0.5)
file_size=440249
# 发送要传输的数据包数量给接收端
file_size_data = struct.pack('i', file_size)
if len(file_size_data) < 300:
    file_size_data += b'\x00' * (300 - len(file_size_data))
ser.write(file_size_data)
ser.close()