from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import http.client, urllib
import json
from zhdate import ZhDate

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
TIANXING_APK=os.environ['TIANXING_APK']
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_ids = os.environ["USER_ID"].split("\n")
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['temp'])


def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days


def get_birthday():
    # 根据生日，首先来确定农历的生日的时候
    date1 = ZhDate(datetime.now().year, 9, 26).to_datetime() #转化为阳历的具体生日。
    if date1 < datetime.now():
        date1 = date1.replace(year=next.year + 1)

    return (date1 - today).days,date1


def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()

    conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': TIANXING_APK})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/caihongpi/index', params, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    return data["newslist"][0]["content"].replace("。", ".")


def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


def get_hot_serch():
    conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': TIANXING_APK})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/networkhot/index', params, headers)
    res = conn.getresponse()
    hot_data = json.loads(res.read().decode('utf-8'))
    hot_list = list()
    hot_list.append(hot_data["newslist"][0]["title"])
    hot_list.append(hot_data["newslist"][1]["title"])
    hot_list.append(hot_data["newslist"][2]["title"])
    return hot_list
def get_xingzuo():
    conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': TIANXING_APK, 'astro': '天蝎座'})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/star/index', params, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode('utf-8'))
    return data

def get_mingyan():
    import http.client, urllib
    conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': TIANXING_APK, 'num': '1'})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/dictum/index', params, headers)
    res = conn.getresponse()
    data =json.loads(res.read().decode('utf-8'))
    return data


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
wea, temperature = get_weather()
hot_list = get_hot_serch()
brith_nong_day,brith_nong=get_birthday()
xingzuo =get_xingzuo()
mingyan=get_mingyan()

data = {
    "weather": {"value": wea},
    "temperature": {"value": temperature},
    "love_days": {"value": get_count()},
    "birthday_left": {"value": brith_nong_day},
    "words": {"value": get_words(),
              "color": get_random_color()},
    "hot_search0": {"value": hot_list[0]},
    "hot_serac": {"value": hot_list[1]},
    "hot_sera": {"value": hot_list[2]},
    "brithday_nong":{"value":str(brith_nong)[0:10],
                     "color":"#173177"},
    "xingzuo":{"value":xingzuo["newslist"][8]["content"]},
    "mingren":{"value":mingyan["newslist"][0]["content"]+" 来自："+mingyan["newslist"][0]["mrname"]}
}

count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1
print(res)
