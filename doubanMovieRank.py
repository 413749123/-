#!/usr/bin/python
#coding:utf-8

import requests
from bs4 import BeautifulSoup as bsp
import urllib
import re
import json

#解决写入文件时编码问题
import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

#消息头,一定程度的反防爬虫机制
HostReferer = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Referer':'https://movie.douban.com/'
}

parameter = {'type':'movie','tag':'科幻','sort':'recommend',
        'page_limit':20,'page_start':0}

session = requests.session()

tagList = ["热门","最新","经典","豆瓣高分","冷门佳片","华语","欧美","韩国","日本","动作","喜剧","爱情","科幻","悬疑","恐怖","治愈"]

sortList = {'推荐':'recommend','时间':'time','评价':'rank'}

count = 1

def usage():

    print u'命令行参数:'+'\t'+'python xxxx.py 类别 排行方式 页数'
    print '\t',u'类别:'
    for tag in tagList:
        print '\t\t'+tag

    print '\t',u'排行方式:'
    for sort in sortList.keys():
        print '\t\t'+sort

def getEncodedUrl(mainUrl,parm):
    return mainUrl + urllib.urlencode(parm)

def getHtmlContent(url):
    html = session.get(url,headers = HostReferer)
    return html.content

def getDetails(sid):
    url = 'https://movie.douban.com/j/subject_abstract?subject_id=' + str(sid)
    content = getHtmlContent(url)
    
    data = json.loads(content)['subject']

    if len(data) > 0:
        return {'duration':data['duration'],'release_year':data['release_year'],
                'region':data['region'],'short_comment':data['short_comment']}

    return None



def getPage(page):
    global count
    url = 'https://movie.douban.com/j/search_subjects?'
    parameter['page_start'] = page * parameter['page_limit']

    url = getEncodedUrl(url,parameter)
    #print url

    content = getHtmlContent(url)
    #print content.decode('utf8')
    data = json.loads(content)
    
    for sub in data['subjects']:
        print str(count),'\t\t\t\t'+u'片名: '+sub['title']
        details = getDetails(sub['id'])
        if details:
            print '\t',u'评分:'+sub['rate']+'\t'+u'发行时间:'+details['release_year']+'\t'+u'时长:'+details['duration']+'\t'+u'地区:'+details['region']

            print '\t',u'短评:'+details['short_comment']['content']
            print '\t\t\t\t\t\t---'+details['short_comment']['author']+'\n'

        count += 1
        

    return len(data['subjects']) > 0
        
def getRankInfo(tag,maxPage,sort):
    global count 
    count = 1
    page = 0
    if tag not in tagList:
        print u'无法获取'+tag+u'榜,请检查输入'
        return
    if sort not in sortList.keys():
        print u'无法按'+sort+u'排序,请检查输入'
        return
    parameter['tag'] = tag
    parameter['sort'] = sortList[sort]
    while True:
        print '\n\t\t\t\t',tag,u'榜-'+u'第'+str(page+1)+u'页    按'+sort+u'排序'+'\n'
        if getPage(page) == False:
            break
        page += 1
        if page >= maxPage:
                break

def main():
    #for tag in tagList:
        #getRankInfo(tag,1)
    tag = u'科幻'
    sort = '推荐'
    page = 1
    if len(sys.argv) > 3:
        page = int(sys.argv[3])
    if len(sys.argv) > 2:
        sort = sys.argv[2]
    if len(sys.argv) > 1:
        s = sys.argv[1]
        if s in ['-h','--help','-help']:
            usage()
            return
        else:
            tag = sys.argv[1]

    getRankInfo(tag,page,sort)
        
main()
