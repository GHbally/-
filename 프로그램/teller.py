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
import noti
import pandas as pd

file_path = "area_codes.xlsx"

# 엑셀 파일 읽기

df = pd.read_excel(file_path, dtype=str, converters={'C': str})

# B 열과 C 열을 사용하여 딕셔너리 생성
area_code_dict = {row['구']: str(row['코드']).zfill(4) for _, row in df.iterrows()}

for key in area_code_dict:
    if len(area_code_dict[key]) == 3:
        area_code_dict[key] = '0' + area_code_dict[key]
# 딕셔너리 확인

print(area_code_dict)
def get_area_code(area_name):
    return area_code_dict.get(area_name, "코드를 찾을 수 없습니다.")

def replyGasData(prod_type, user, loc_param='00'):
    print(user, prod_type, loc_param)
    res_list = noti.getData( prod_type, loc_param )
    msg = ''
    for r in res_list:
        print( str(datetime.now()).split('.')[0], r )
        if len(r+msg)+1>noti.MAX_MSG_LENGTH:
            noti.sendMessage( user, msg )
            msg = r+'\n'
        else:
            msg += r+'\n'
    if msg:
        noti.sendMessage( user, msg )
    else:
        noti.sendMessage( user, '%s 잘못된 질못 형식입니다.')

def save( user, loc_param ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    try:
        cursor.execute('INSERT INTO users(user, location) VALUES ("%s", "%s")' % (user, loc_param))
    except sqlite3.IntegrityError:
        noti.sendMessage( user, '이미 해당 정보가 저장되어 있습니다.' )
        return
    else:
        noti.sendMessage( user, '저장되었습니다.' )
        conn.commit()

def check( user ):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users( user TEXT, location TEXT, PRIMARY KEY(user, location) )')
    cursor.execute('SELECT * from users WHERE user="%s"' % user)
    for data in cursor.fetchall():
        row = 'id:' + str(data[0]) + ', location:' + data[1]
        noti.sendMessage( user, row )


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        noti.sendMessage(chat_id, '난 텍스트 이외의 메시지는 처리하지 못해요.')
        return

    text = msg['text']
    args = text.split(' ')

    if text.startswith('전국') and len(args) > 1:
        print('try to 전국', args[1])
        if args[1] == '휘발유':
            replyGasData('B027', chat_id)
        elif args[1] == '경유':
            replyGasData('D047', chat_id)
    elif text.startswith('지역') and len(args) > 1:
        print('try to 지역', args[1],args[2])
        # 지역 이름을 시군코드로 변환
        area_code = get_area_code(args[1])
        if area_code != "코드를 찾을 수 없습니다.":
            if len(args) > 2 and args[2] == '휘발유':
                replyGasData('B027', chat_id, area_code)
            elif len(args) > 2 and args[2] == '경유':
                replyGasData('D047', chat_id, area_code)
            else:
                noti.sendMessage(chat_id, '올바른 기름 종류를 입력하세요. (휘발유 또는 경유)')
        else:
            noti.sendMessage(chat_id, '해당 지역의 코드를 찾을 수 없습니다.')
    elif text.startswith('저장') and len(args) > 1:
        print('try to 저장', args[1])
        save(chat_id, args[1])
    elif text.startswith('확인'):
        print('try to 확인')
        check(chat_id)
    else:
        noti.sendMessage(chat_id, '모르는 명령어입니다.\n지역 [기름 종류]을 입력해주세요')


today = date.today()
current_month = today.strftime('%Y%m')

print( '[',today,']received token :', noti.TOKEN )

bot = telepot.Bot(noti.TOKEN)
pprint( bot.getMe() )

bot.message_loop(handle)

print('Listening...')

while 1:
  time.sleep(10)