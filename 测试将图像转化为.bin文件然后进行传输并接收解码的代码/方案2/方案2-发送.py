import serial
from PIL import Image
import struct

# 打开彩色图像
img = Image.open('1.jpg')

# 转换为RGB格式
img = img.convert('RGB')

# 获取图像的宽度和高度
width, height = img.size
data=(width,height)
# 创建二进制文件并写入宽度和高度的值
with open('方案2_output.bin', 'wb') as f:

    f.write(struct.pack('2i', width, height))
    print(f.tell())

    # 循环遍历图像的每个像素，并将RGB值写入二进制文件
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            f.write(struct.pack('BBB', r, g, b))

