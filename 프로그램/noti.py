#!/usr/bin/python
# coding=utf-8

import sys
import time
import sqlite3
import telepot
from pprint import pprint
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import date, datetime, timedelta
import traceback
import lxml

key = 'F240513145' #'여기에 API KEY를 입력하세요'
TOKEN = '7171825505:AAHfB2d2MRtKfuJYxt0BeBbEa0fBDHAxbqA' #'여기에 텔레그램 토큰을 입력하세요'
MAX_MSG_LENGTH = 300
baseurl = 'http://www.opinet.co.kr/api/lowTop10.do?out=xml&code='+key
bot = telepot.Bot(TOKEN)

#XXXXXX&prodcd=B027&area=0101&cnt=2

def getData(prod_type, loc_param='1508'):
    res_list = []
    url = baseurl + '&prodcd=' + prod_type + '&area=' + loc_param + '&cnt=20'
    res_body = urlopen(url).read()
    soup = BeautifulSoup(res_body, 'lxml-xml')  # 여기서 lxml-xml 파서를 사용합니다.
    items = soup.findAll('OIL')  # 'item' 대신 'oil' 태그로 변경
    cnt = 0
    for item in items:
        price = item.find('PRICE').text
        new_adr = item.find('NEW_ADR').text
        os_nm = item.find('OS_NM').text
        row = str(cnt+1)+ '위 ' + f'이름: {os_nm}, 가격: {price}, 주소: {new_adr}'
        res_list.append(row)
        cnt = cnt +1
    return res_list
def sendMessage(user, msg):
    try:
        bot.sendMessage(user, msg)
    except:
        traceback.print_exc(file=sys.stdout)


def sendWelcomeMessage(user):
    msg = ("안녕하세요 주유도사 봇입니다.\n"
           "전국 + 기름 종류 or 지역 + 지역이름(시, 군, 구) + 기름 종류를 입력하여\n"
           "지역 내 싼 주유소 정보들을 확인하세요!")
    sendMessage(user, msg)

def run(date_param, param='11710'):
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS logs( user TEXT, log TEXT, PRIMARY KEY(user, log) )')
    conn.commit()

    user_cursor = sqlite3.connect('users.db').cursor()
    user_cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    user_cursor.execute('SELECT * from users')

    for data in user_cursor.fetchall():
        user, param = data[0], data[1]
        print(user, date_param, param)
        res_list = getData( param, date_param )
        msg = ''
        for r in res_list:
            try:
                cursor.execute('INSERT INTO logs (user,log) VALUES ("%s", "%s")'%(user,r))
            except sqlite3.IntegrityError:
                # 이미 해당 데이터가 있다는 것을 의미합니다.
                pass
            else:
                print( str(datetime.now()).split('.')[0], r )
                if len(r+msg)+1>MAX_MSG_LENGTH:
                    sendMessage( user, msg )
                    msg = r+'\n'
                else:
                    msg += r+'\n'
        if msg:
            sendMessage( user, msg )
    conn.commit()

if __name__=='__main__':
    today = date.today()
    current_month = today.strftime('%Y%m')

    print( '[',today,']received token :', TOKEN )

    pprint( bot.getMe() )

    run(current_month)
