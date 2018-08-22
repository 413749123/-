#!/usr/bin/python
#coding=utf-8

import os
import re
import json
import requests
from bs4 import BeautifulSoup as bsp
#解决写入文件时编码问题
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

session = requests.session()#维护session

#消息头,一定程度的反防爬虫机制
HostReferer = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Referer':'https://www.bilibili.com/'
}

#排行榜不同 分区不同 排行周期不同
rankDic = {'全站':'all'}
partDic = {'全站':'0','动画':'1','国创':'168','音乐':'3',
        '舞蹈':'129','科技':'36','游戏':'4','娱乐':'5','鬼畜':'119',
        '影视':'181','时尚':'155','生活':'160'}
timeList = {1:'日榜',3:'三日榜',7:'周榜',30:'月榜'}

#根据参数构造url
def urlConstructor(rankType,partition,rankTime):
    url = 'http://www.bilibili.com/ranking/'+rankDic[rankType]+'/'+partDic[partition]+'/0/'+str(rankTime)
    # 1 为日榜 3 为三日榜 7 为周榜 30 为月榜
    return url

#暂时无用
def getHtml(url):
    html = session.get(url,headers = HostReferer)
    html = html.text
    return html

#获取视频播放量和弹幕数(danmaku)
#原本用av号链接获取，发现没用，后来找到接口
def getVideoView(url):
    #提取av号
    aid = re.findall(r'av([\d]+)',url)
    aid = aid[0]
    url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid='+aid
    html = session.get(url,headers = HostReferer).content
    info = json.loads(html)
    
    return info['data']
        
#获取单个排行的榜单数据
def getRankData(partition,rankTime):
    #url = 'https://www.bilibili.com/ranking?spm_id_from=333.334.banner_link.1'
    url = urlConstructor('全站',partition,rankTime) 

    result = bsp(session.get(url,headers = HostReferer).content,'lxml')
    #将结果转化为bsp结构

    items = result.find_all('div',class_ = 'info')
    
    rankData = ''
    count = 1
    for item in items:
        detail = item.find_all('span')
        pts = item.find_all('div',class_ = 'pts')
        if detail:
            #获取该视频链接
            videoHref = item.a['href']
            #通过链接获取播放量和弹幕数
            data = getVideoView('http:'+videoHref)
            rankData += str(count)+u'\t标题: '+item.a.text + '\n'
            rankData += u'\t播放量: '+str(data['view'])+u'\t弹幕数: '+str(data['danmaku']) + '\t'+u'UP主: '+detail[1].text+'\t' + u'综合得分: '+pts[0].div.text+'\n\n'
            count += 1
        
        #break#调试先设置只执行一次
    return rankData

#获取全站榜所有分区的排行数据
def getAllRankData():
    name = 'bilibili全站榜'

    os.mkdir(name)
    for key in partDic:
        for rankTime in timeList:
            print u'正在获取'+key+'-'+timeList[rankTime]+' 信息...'
            rankData = getRankData(key,rankTime)
         # print rankData
            with open(name+'/'+key+'-'+timeList[rankTime]+'.txt','w') as f:
                f.write(rankData)
        
def main():
    partition = '鬼畜'
    rankTime = 1
    if len(sys.argv) > 1:
        partition = sys.argv[1]
        if len(sys.argv) > 2:
            rankTime = int(sys.argv[2])
    rankData = getRankData(partition,rankTime)
    print '\t\t\t\t\t',partition+'-'+timeList[rankTime]+'\n'
    print rankData

main()
