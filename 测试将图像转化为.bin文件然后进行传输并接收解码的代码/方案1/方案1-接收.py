import serial
import time
import io
from PIL import Image


ser = serial.Serial('COM2', 115200)  # 串口初始化，需要根据实际情况修改端口和波特率

buffer = io.BytesIO()  # 用于缓存接收到的数据

while True:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)  # 读取串口接收到的所有数据
        buffer.write(data)  # 将数据写入缓存
        time.sleep(0.01)  # 等待一段时间，避免数据接收过快

    if buffer.tell() >= 26938:  # 如果接收到的数据长度达到图片的长度
        buffer.seek(0)  # 将缓存指针移到起始位置
        img_data = buffer.read()  # 读取缓存中的数据
        img = Image.open(io.BytesIO(img_data))  # 用PIL库打开图像
        img.save("666.jpg")
        buffer = io.BytesIO()  # 清空缓存
        ser.close()
        print("接收完毕")
