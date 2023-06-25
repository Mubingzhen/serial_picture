import serial
from PIL import Image
import struct
import io
# 打开串口连接
#ser = serial.Serial('/dev/ttyUSB0', 9600)
with open('方案2_output.bin', 'rb') as f:
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
img.save('方案2_restored_image.jpg')