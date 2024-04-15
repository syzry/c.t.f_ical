from datetime import datetime, timedelta
import feedparser
import re
import hashlib
import requests
import json

cn_ctf_url = 'https://raw.githubusercontent.com/ProbiusOfficial/Hello-CTFtime/main/CN.json'

rssUpcoming = 'https://ctftime.org/event/list/upcoming/rss/'
rssActive = 'https://ctftime.org/event/list/archive/rss/'
rssNowrunning = 'https://ctftime.org/event/list/running/rss/'


def get_md5(s):
    md = hashlib.md5()
    md.update(s.encode('utf-8'))
    return md.hexdigest()

def fetch_cn_ctf_data(url):
    # 使用POST请求获取国内CTF数据
    headers = {
    'user-agent': 'Mozilla/0.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
    }
    response = requests.get(url,headers=headers)
    res_json=response.json()["data"]["result"]
    events=[]
    for i in res_json:
        start_date=datetime.strptime(i['bsks'], '%Y年%m月%d日 %H:%M')- timedelta(hours=8)
        finish_date=datetime.strptime(i['bsjs'], '%Y年%m月%d日 %H:%M')- timedelta(hours=8)
        eventData= {
                    'BEGIN':'VEVENT',
                    'SUMMARY':i['name'],
                    'DTSTART':start_date.strftime("%Y%m%dT%H%M%SZ"),
                    'DTEND':finish_date.strftime("%Y%m%dT%H%M%SZ"),
                    'UID':get_md5(i['name']+start_date.strftime("%Y%m%dT%H%M%SZ")),
                    'VTIMEZONE':'Asia/Shanghai',
                    'DTSTAMP':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    'CREATED':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    'URL':i['link'],
                    'DESCRIPTION':i['type']+' | '+i['link']+' | '+'比赛ID - '+str(i['id'])+' | '+'报名---'+i['bmks']+'-'+i['bmjz']+'-备注-'+re.sub(r"\s+", "", i['readmore']),
                    'END':'VEVENT'
                }
        events.append(eventData)
    return events

def fetch_global_ctf_content(rss_url):
    feed = feedparser.parse(rss_url)
    events = []  
    try:
        feedTitle = feed['feed']['title']
    except KeyError:
        print('RSS源解析失败，请检查URL是否正确')

    for entry in feed.entries:

        eventName = entry.title

        # 时间处理部分
        start_date = datetime.strptime(entry.start_date, '%Y%m%dT%H%M%S')
        finish_date = datetime.strptime(entry.finish_date, '%Y%m%dT%H%M%S')


        # 主办方部分
        organizers_data = json.loads(entry.organizers)
        organizers_names = []
        organizers_urls = []
        for organizer in organizers_data:
            name = organizer['name']
            url = 'https://ctftime.org/team/' + str(organizer['id'])
            organizers_names.append(name)
            organizers_urls.append(url)
        organizers_names_str = ', '.join(organizers_names)
        organizers_urls_str = ', '.join(organizers_urls)

        eventUrl = entry.url
        eventName = f'{eventName}'
        eventType = entry.format_text
        eventWeight = entry.weight
        eventOrganizers =  f'{organizers_names_str} ({organizers_urls_str})'
        
        eventData= {
                    'BEGIN':'VEVENT',
                    'SUMMARY':eventName,
                    'DTSTART':start_date.strftime("%Y%m%dT%H%M%SZ"),
                    'DTEND':finish_date.strftime("%Y%m%dT%H%M%SZ"),
                    'UID':get_md5(eventName+start_date.strftime("%Y%m%dT%H%M%SZ")),
                    'VTIMEZONE':'Asia/Shanghai',
                    'DTSTAMP':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    'CREATED':datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    'URL':eventUrl,
                    'DESCRIPTION':eventType+' | '+eventUrl+' | '+'比赛权重 - '+str(eventWeight)+' | '+'比赛ID - '+str(entry.ctf_id)+' | '+'赛事主办 - '+eventOrganizers,
                    'END':'VEVENT'
                }
        events.append(eventData)

    return events

upcoming_events = fetch_global_ctf_content(rssUpcoming)
active_events = fetch_global_ctf_content(rssActive)
running_events = fetch_global_ctf_content(rssNowrunning)

all_events = upcoming_events + running_events + active_events 
with open('Global.txt', 'w', encoding='utf-8') as file:
    file.write('BEGIN:VCALENDAR\n')
    for i in all_events:
        for j,k in i.items():
            file.write(j+':'+k+'\n')
    file.write('END:VCALENDAR')

# cn_ctf_data = fetch_cn_ctf_data(cn_ctf_url)
# with open('CN.txt', 'w', encoding='utf-8') as file:
#     file.write('BEGIN:VCALENDAR\n')
#     for i in cn_ctf_data:
#         for j,k in i.items():
#             file.write(j+':'+k+'\n')
#     file.write('END:VCALENDAR')

print("数据抓取完成，保存为 CN.json 和 Global.json")
