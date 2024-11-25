from DrissionPage import ChromiumPage, ChromiumOptions
import os_utils
import drissionpage_utils
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from concurrent.futures import wait
import threading
import json
import os
import re
import sys
tab_activation_lock = threading.Lock()
def 读配置文件():
    # 获取exe所在目录或脚本所在目录 打包要加上--data
    if getattr(sys, 'frozen', False):
        # 打包后的exe目录
        程序目录 = os.path.dirname(sys.executable)
        os_utils.写入本次运行日志(f'打包exe成功从{程序目录}读取配置文件')
    else:
        # 开发环境下的脚本目录
        程序目录 = os.path.dirname(os.path.abspath(__file__))
        os_utils.写入本次运行日志(f'开发环境成功从{程序目录}读取配置文件')
    
    配置文件路径 = os.path.join(程序目录, 'config.json')
    
    try:
        with open(配置文件路径, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f'成功从{配置文件路径}读取配置文件')
            return config
    except Exception as e:
        raise FileNotFoundError(f'读取配置文件失败，请确保config.json与程序在同一目录: {str(e)}')
config=读配置文件()
def 初始化dp():
    co = ChromiumOptions().set_local_port(9222)
    co.set_timeouts(base=5)
    page = ChromiumPage(addr_or_opts=co)
    return page
page=初始化dp()

雨课堂url="https://www.yuketang.cn/v2/web/index"

def 处理单个视频(id):
    global config
    tab = page.new_tab()
    tab.get(f'https://www.yuketang.cn/v2/web/xcloud/video-student/{id}')
    是否已经完成视频=tab.ele('text=已完成')
    if 是否已经完成视频:
        tab.close()
        return f'早已完成视频：https://www.yuketang.cn/v2/web/xcloud/video-student/{id}'
    with tab_activation_lock:
        if drissionpage_utils.判断当前tab是不是video(tab):
            page.activate_tab(tab)
            time.sleep(1)
            切入视频结果 = drissionpage_utils.切入视频(tab)
            if 切入视频结果=='ok':pass
            else:
                tab.close()
                return 切入视频结果
        else:
            tab.close()
            return f'https://www.yuketang.cn/v2/web/xcloud/video-student/{id}：当前页面不是视频页面'
    时间最大上限=config['视频时间最大上限']
    计时=0
    等待时间=5
    try:
        while True:
            if 计时>时间最大上限:
                tab.close()
                return '超时'
            已完成元素=tab.ele('text=已完成')
            if 已完成元素:
                tab.close()
                return '已完成视频'
            try:        
                进度条=tab.ele('.xt_video_player_seek_handle no_drag')
                if 进度条:
                    进度条style=进度条.attr('style')
                    进度百分比=re.search(r'\d+(\.\d+)?', 进度条style)
                    if 进度百分比:
                        if float(进度百分比.group())>=100:
                            tab.close()
                            return '已完成视频'
            except Exception as e:
                return '错误：'+str(e)
            time.sleep(等待时间)
            计时+=等待时间
    except Exception as e:
        tab.close()
        return '错误：'+str(e)

def 获取单个课程未完成视频id(要找的课程):
    tab=page.new_tab()
    tab.get('https://www.yuketang.cn/v2/web/index')
    tab.ele('text=我听的课').click()
    os_utils.写入本次运行日志('开始获取'+要找的课程+'未完成视频id')
    drissionpage_utils.找一个课程元素(tab,要找的课程).click()
    # 开始监听
    tab.listen.start('lms/learn/course/chapter')
    tab.ele('text=学习内容').click()
    数据包=drissionpage_utils.获取数据包(tab)
    所有视频id=[]
    for i in 数据包:
        # 时间表url='https://www.yuketang.cn/mooc-api/v1/lms/learn/course/schedule'
        # 时间表= i.response.body['data']['leaf_schedules']
        videourl="https://www.yuketang.cn/mooc-api/v1/lms/learn/course/chapter"
        if i.url.startswith(videourl):
            course_chapter=i.response.body['data']['course_chapter']
            for i in course_chapter:
                list1=i['section_leaf_list']
                for j in list1:
                    # 判断里面有没有leaf_list
                    if 'leaf_list' in j:
                        for k in j['leaf_list']:
                            所有视频id.append(k['id'])
            break
    过滤出前缀id= (tab.url.split('?')[0]).split('/')[-1]
    加上前缀的视频id=[]
    os_utils.写入本次运行日志('获取'+要找的课程+'所有视频id完成，结果为：'+str(所有视频id))
    for k in 所有视频id:
        加上前缀的视频id.append(f'{过滤出前缀id}/{k}')
    tab.close()
    return 加上前缀的视频id


def 获取所有要刷的课程及各种信息(要找的):
    # 要找的=["科研","英文","外国语"]
    os_utils.写入本次运行日志('开始获取所有要刷的课程及各种信息，课程为：'+','.join(要找的))
    with ThreadPoolExecutor(max_workers=len(要找的)) as pool:
        结果 = [pool.submit(获取单个课程未完成视频id,要找的[i]) for i in range(len(要找的))]
    
    最终结果 = [future.result() for future in as_completed(结果)]
    os_utils.写入本次运行日志('获取所有要刷的课程及各种信息完成，结果为：'+str(最终结果))
    最终结果展平=[i for j in 最终结果 for i in j]
    os_utils.写入本次运行日志('总共有xxx个可能是视频需要刷：'+str(len(最终结果展平)))
    return 最终结果展平


def 多线程刷视频时长(线程数,要找的课程):
    ids=获取所有要刷的课程及各种信息(要找的课程)

    with ThreadPoolExecutor(max_workers=线程数) as pool:
        futures = [pool.submit(处理单个视频, i) for i in ids]
        for future in as_completed(futures):
            os_utils.写入本次运行日志(f'任务完成，结果：{future.result()}')


if __name__ == '__main__':
    os_utils.如果本次运行日志文件不存在则创建()
    os_utils.清空本次运行日志()
    # 切入视频(page)
    # 测试单个()    
    # 测试1()
    #"科研","英文",
    多线程刷视频时长(线程数=config['线程数'],要找的课程=config['要找的课程'])

