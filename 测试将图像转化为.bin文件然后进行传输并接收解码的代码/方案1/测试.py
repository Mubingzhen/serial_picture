from tkinter import filedialog
import struct
from PIL import Image

file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg;*.gif")])
if file_path:
  # 通过PIL库中的Image打开选择的图片文件
  img = Image.open(file_path)
  # 转换为RGB格式
  img = img.convert('RGB')

  # 获取图像的宽度和高度
  width, height = img.size

  # 计算需要传输的数据包数量
  num_packets = ((width * height * 3 + 150 - 1) // 150) - 1
  print(f'num_packets={num_packets}')
  # 创建二进制文件并写入宽度和高度的值
  with open('方案5_output.bin', 'wb') as f:
      f.write(struct.pack('2i', width, height))

      # 循环遍历图像的每个像素，并将RGB值写入二进制文件
      for y in range(height):
          for x in range(width):
              r, g, b = img.getpixel((x, y))
              f.write(struct.pack('BBB', r, g, b))
