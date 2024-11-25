import time
from DrissionPage.common import Actions



def 通用等待(检查函数, 错误信息, 超时=10):
    剩余时间 = 超时
    while True:
        try:
            if 检查函数():
                break
            time.sleep(1)
            剩余时间 -= 1
            if 剩余时间 < 0:
                raise Exception(f"{错误信息}，超时{超时}秒，退出循环。")
        except Exception as e:
            if 剩余时间 < 0:
                raise e
            time.sleep(1)
            剩余时间 -= 1

def 等待元素加载完成(元素, 条件:str, 超时=10):
    """等待页面元素加载完成"""
    def 检查元素存在():
        元素.ele(条件)
        return True
    
    通用等待(
        检查元素存在,
        f"等待元素加载完成：{条件}",
        超时
    )

def 等待跳转到指定页面(元素, 目标url列表, 超时=10):
    """等待页面跳转到目标URL"""
    def 检查页面URL():
        if 元素.url in 目标url列表:
            return True
        return False
    
    通用等待(
        检查页面URL,
        f"等待跳转目标页面：{元素.url}",
        超时
    )

def 打开指定页面并等待跳转到指定页面(元素, 目标url):
    打开页面(元素, 目标url)
    等待跳转到指定页面(元素, [目标url])

def 打开页面(元素, 目标url):
    元素.get(目标url)

def 找一个元素(元素, 条件:str):
    try:
        元素=元素.ele(条件)
        return 元素
    except:
        return None

def 找多个元素(元素, 条件:str):
    return 元素.eles(条件)

def 获取元素文本(元素):
    return 元素.text.strip()

def 获取元素地址(元素):
    return 元素.link

def 找一个元素的属性(元素, 条件, 属性):
    try:
        if 条件==None:
            return 元素.attr(属性)
        else:
            return 找一个元素(元素,条件).attr(属性)
    except:
        return None

def 找一个元素的文本(元素,条件:str):
    return 找一个元素的属性(元素,条件,'text')

def 创建多个标签页对象(元素,标签页数量=5):
    return [元素.new_tab() for _ in range(标签页数量)]

def 开始监听数据包(元素):
    元素.listen.start()

def 获取数据包(元素):
    '''
    获取数据包,返回一个可迭代对象
    '''
    return 元素.listen.steps()

def 结束监听数据包(元素):
    元素.listen.stop()

def 点击播放按钮(tab):
    播放按钮=找一个元素(tab,'.xt_video_player_play_btn fl')
    播放按钮.click()
def 点击暂停按钮(tab):
    暂停按钮=找一个元素(tab,'.xt_video_player_play_btn fl xt_video_player_play_btn_pause')
    if 暂停按钮:
        return 暂停按钮.click()
def 呼出bar(tab):
    bar=找一个元素(tab,'.xt_video_player_controls_inner')
    if bar:
        return bar.click()
def 二倍数(tab):
    # 先选中tab
    倍速=找一个元素(tab,'.xt_video_player_speed xt_video_player_common fr')
    二倍速=找一个元素(tab,'text:2.00X')
    ac=Actions(tab)
    ac.move_to(倍速).move_to(二倍速).click()

def 点音量(tab):
    音量=找一个元素(tab,'.xt_video_player_common_icon')
    ac=Actions(tab)
    ac.move_to(音量).click()
    
def 判断当前tab是不是video(tab):
    if 找一个元素(tab,'#video-box'):
        return True
    else:
        return False
    

def 请求视频链接(tab,id):
    前置='https://www.yuketang.cn/v2/web/xcloud/video-student/23223882/'
    tab.get(前置+str(id))


def 切入视频(tab):
    try:
        呼出bar(tab)
        二倍数(tab)
        点音量(tab)
        点击播放按钮(tab)
        return 'ok'
    except Exception as e:
        return f'切入视频发生错误:{str(e)}'
    

def 找一个课程元素(tab,要找的文本):
    return tab.ele('tag:h1'+'@@text():'+要找的文本)






