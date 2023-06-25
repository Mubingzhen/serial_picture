import serial
from threading import Thread

# 串口实例化
ser = serial.Serial('COM1', 115200)

"""
in_waiting:
Return the number of bytes currently in the input buffer

out_waiting:
Return the number of bytes currently in the output buffer.
"""

# 定义发送请求的函数，命令语句是按接收端要求来的
def send(n):
    for i in range(n):
        ser.write("r vbus_voltage\n".encode('ascii'))
        ser.write("r axis0.motor.config.current_lim\n".encode('ascii'))
        ser.write("r axis0.controller.config.vel_limit\n".encode('ascii'))
        ser.write("r axis0.controller.config.control_mode\n".encode('ascii'))
    print(f"{n} times sent...")
# 用线程来控制发送 n 次
thread_send = Thread(target=lambda: send(800))
# 启动线程
thread_send.start()
# 等待线程结束
thread_send.join()
# 打印此时输入端缓存字节数
print(ser.in_waiting)
