import time
import os
import sys

def 获取程序目录():
    if getattr(sys, 'frozen', False):
        # 打包后的程序，使用可执行文件所在目录
        return os.path.dirname(sys.executable)
    else:
        # 直接运行的Python脚本，使用脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

当前目录 = 获取程序目录()

# 写入日志文件
def 写入本次运行日志(message):
    日志文件路径 = os.path.join(当前目录, '本次运行日志.txt')
    with open(日志文件路径, 'a', encoding='utf-8') as f:
        f.write(f'当前时间：{time.strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write(f'{message}\n')
        f.write('\n')

def 清空本次运行日志():
    日志文件路径 = os.path.join(当前目录, '本次运行日志.txt')
    with open(日志文件路径, 'w', encoding='utf-8') as f:
        f.write('')

def 如果本次运行日志文件不存在则创建():
    日志文件路径 = os.path.join(当前目录, '本次运行日志.txt')
    if not os.path.exists(日志文件路径):
        with open(日志文件路径, 'w', encoding='utf-8') as f:
            f.write('')

