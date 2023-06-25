import serial
import struct

# 打开串口连接
ser = serial.Serial('COM2', 115200)

# 从串口接收数据
data = ser.read(300)

# 解包数据
a= struct.unpack('i', data[0:4])

# 关闭串口连接
ser.close()

# 输出接收到的数据
print(f"a={a}")
