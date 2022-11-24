from ast import If
import os
from datetime import datetime
import json
import copy
from re import X
import time
import datetime
import requests
import random
from math import*
from bs4 import BeautifulSoup
from requests.api import get
from serpapi import GoogleSearch
import googletrans
from googlesearch import search
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tweepy
import pyimgur
import matplotlib.pyplot as plt
import os


from flask import Flask, abort, request

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent,
                            TextMessage,
                            TextSendMessage,
                            ImageSendMessage,
                            VideoSendMessage,
                            AudioSendMessage,
                            LocationSendMessage,
                            StickerSendMessage,
                            ImagemapSendMessage,
                            TemplateSendMessage,
                            FlexSendMessage,
                            ButtonsTemplate,
                            MessageTemplateAction,
                            PostbackEvent,
                            PostbackTemplateAction)

send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"}

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


Message_counter = 0
Message_container = ['A', 'B']
Message_send = ''


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    dt = (datetime.datetime.today() +
          datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
    print(dt)

    get_message = event.message.text.rstrip()
    get_message = get_message.replace('！', '!')
    l_get_message = get_message.strip()
    split = get_message.split()

    id = event.source.user_id
    owner = 'U2290158f54f16aea8c2bdb597a54ff9e'
    try:
        group_id = event.source.group_id
    except:
        group_id = 'N/A'
    group = 'C0862e003396d3da93b9016d848560f29'

    line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
    try:
        profile = line_bot_api.get_group_member_profile(
            group_id, id)
    except:
        profile = line_bot_api.get_profile(id)
    user_name = profile.display_name

    global Message_counter
    global Message_container
    global Message_send
    Message_counter += 1
    if(Message_counter % 3 == 2):
        Message_container[0] = get_message
    elif(Message_counter % 3 == 1):
        Message_container[0] = get_message
    else:
        Message_container[1] = get_message

# {"message": {"id": "14426028129997", "text": "!\u5211\u5b89", "type": "text"}, "mode": "active", "replyToken": "2b10e43d55ac4b53b4cad4730f3ec57c", "source": {"groupId": "C0862e003396d3da93b9016d848560f29", "type": "group", "userId": "U2290158f54f16aea8c2bdb597a54ff9e"}, "timestamp": 1626764061203, "type": "message"}
# id = U2290158f54f16aea8c2bdb597a54ff9e
    # Send To Line
    print(user_name+id)

    def text_reply(content):
        reply = TextSendMessage(text=content)
        line_bot_api.reply_message(event.reply_token, reply)

    def img_reply(URL):
        reply = ImageSendMessage(
            original_content_url=URL, preview_image_url=URL)
        line_bot_api.reply_message(event.reply_token, reply)

    def audio_reply(URL):
        reply = AudioSendMessage(
            original_content_url=URL, duration=100000)
        line_bot_api.reply_message(event.reply_token, reply)

    def video_reply(URL, URL2):
        reply = VideoSendMessage(
            original_content_url=URL, preview_image_url=URL2)
        line_bot_api.reply_message(event.reply_token, reply)

    def sheet_reload(key):
        scopes = ["https://spreadsheets.google.com/feeds"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "json/credentials.json", scopes)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(key).sheet1
        return sheet

    def bully_reload():
        sheet = sheet_reload("1GmO4ygrYvr2fv7z-PuFZZegQDt694PyMidHL3KWEHU4")
        bullyData = sheet.get_all_values()
        bully_names = [bullyData[i][0]
                       for i in range(len(bullyData))]
        bully_p = [bullyData[i][1]
                   for i in range(len(bullyData))]
        words = [bullyData[i][2]
                 for i in range(len(bullyData))]
        bully_words = []
        for i in words:
            bully_words.append(i.split(','))
        return sheet, bully_names, bully_p, bully_words

    def bully(n, List):
        if n > 0:
            randNum = random.randint(1, n)
            if randNum == 1:
                text = random.choice(List)
                text_reply(text)

    if group_id == group:
        CLIENT_ID = "14dcbae49ad6b84"
        sheet = sheet_reload("1ti_4scE5PyIzcH4s6mzaWaGqiIQfK9X_R--oDXqyJsA")
        data = sheet.get_all_values()
        dates = [data[i][0]for i in range(len(data))]
        times = [data[i][1]for i in range(len(data))]
        dt = (datetime.datetime.today() +
              datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
        if dt not in dates:
            sheet.append_row([dt, '1'])
            t = 0
            X = []
            Y = []
            for i in range(1, 15):
                if(t == 7):
                    break
                if(dates[-i] in X):
                    Y[len(Y)-1] += times[-i]
                else:
                    X.append(dates[-i][5:])
                    Y.append(int(times[-i]))
                    t += 1
            X.reverse()
            Y.reverse()
            plt.plot(X, Y)
            plt.title("Message Counting(only text)")
            for a, b in zip(X, Y):
                plt.text(a, b, b, ha='center', va='bottom', fontsize=12)
            plt.savefig("test.jpg")
            PATH = "test.jpg"  # A Filepath to an image on your computer"
            title = "Uploaded with PyImgur"
            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title=title)
            os.remove("test.jpg")
            img_reply(uploaded_image.link)
        else:
            n = int(times[dates.index(dt)])
            sheet.update_cell(dates.index(dt)+1, 2, str(n+1))

    if id == owner:
        if split[0] == '!bully':
            sheet, bully_names, bully_p, bully_words = bully_reload()
            if len(split) == 2:
                if split[1] == 'list':
                    keys = ""
                    for i in range(len(bully_names)):
                        if int(bully_p[i]) != 0:
                            keys += bully_names[i]+'\n'
                    text_reply(f'名單:\n{keys}')
                elif split[1] in bully_names:
                    p = bully_p[bully_names.index(split[1])]
                    words = bully_words[bully_names.index(split[1])]
                    text_reply(f'p:{p}\nwords:\n{words}')
                else:
                    text_reply(f'名單無此人')
            elif split[2] == 'p':
                if split[1] in bully_names:
                    bully_p[bully_names.index(split[1])] = split[3]
                    sheet.update_cell(bully_names.index(
                        split[1])+1, 2, split[3])
                    text_reply(f'{split[1]}的被霸凌機率已調整為1/{split[3]}')
                else:
                    sheet.append_row([split[1], split[3], f'{split[1]}去死'])
                    text_reply(f'{split[1]}未登錄霸凌名單，現已登錄且將被霸凌機率設為1/{split[3]}')
            elif split[2] == '+':
                if split[1] in bully_names:
                    if split[3] not in bully_words[bully_names.index(split[1])]:
                        bully_words[bully_names.index(
                            split[1])].append(split[3])
                        words = ''
                        for i in bully_words[bully_names.index(split[1])]:
                            words += ','+str(i)
                        sheet.update_cell(
                            bully_names.index(split[1])+1, 3, words[1:])
                        text_reply(
                            f'資料庫已加入「{split[3]}」\n現已收錄:{bully_words[bully_names.index(split[1])]}')
                    else:
                        text_reply('此句已存在')
                else:
                    sheet.append_row([split[1], '5', split[3]])
                    text_reply(f'{split[1]}未登錄霸凌名單\n現已登錄且收錄:[\'{split[3]}\']')
            elif split[2] == '-':
                if split[1] in bully_names:
                    if split[3] in bully_words[bully_names.index(split[1])]:
                        bully_words[bully_names.index(
                            split[1])].remove(split[3])
                        words = ''
                        for i in bully_words[bully_names.index(split[1])]:
                            words += ','+str(i)
                        sheet.update_cell(
                            bully_names.index(split[1])+1, 3, words[1:])

                        text_reply(
                            f'資料庫已刪除「{split[3]}」\n現已收錄:{bully_words[bully_names.index(split[1])]}')
                    else:
                        text_reply('此句不存在')
                else:
                    text_reply(f'{split[1]}未登錄霸凌名單')
            elif split[2] == 'del':
                if split[1] in bully_names:
                    bully_p[bully_names.index(split[1])] = '0'
                    sheet.update_cell(bully_names.index(
                        split[1])+1, 2, '0')
                    keys = ""
                    for i in range(len(bully_names)):
                        if int(bully_p[i]) != 0:
                            keys += bully_names[i]+'\n'
                    text_reply(f'成員已移除{split[1]}\n目前名單:\n{keys}')
                else:
                    text_reply(f'成員名單不存在{split[1]}')

    with open('json/setting.json', 'r', encoding='utf8') as jfile:
        jdata = json.load(jfile)

    if split[0].lower() == '!t':
        translator = googletrans.Translator()
        text = get_message[3:]
        if text == '?':
            trans = str(googletrans.LANGCODES)[1:-1].replace(', ', '\n')
        elif split[1] in googletrans.LANGCODES.values() and len(split) != 2:
            text = get_message[6:]
            trans = translator.translate(text, dest=split[1]).text
        else:
            trans = translator.translate(text, dest='zh-tw').text
        text_reply(trans)

    if get_message[:5] == '!eval':
        content = str(eval(get_message[6:]))
        text_reply(content)

    if get_message == '!irin':
        random_pic = random.choice(jdata['irin_pic'])
        img_reply(random_pic)

    if get_message == '!刑安':
        print(event)
        random_pic = random.choice(jdata['刑安_pic'])
        img_reply(random_pic)

    if get_message == '!抽卡':
        img_reply(
            'https://cdn.discordapp.com/attachments/856516846144192543/866531135126110248/14419370570913.jpg')

    if get_message[:2] == '!抽':
        content = ''
        try:
            member_list = jdata[group_id]
            if split[-1].isdigit() and int(split[-1]) <= len(member_list):
                n = int(split[-1])
            elif split[-1].isdigit() and int(split[-1]) > len(member_list):
                n = len(member_list)
            else:
                n = 1
            for i in range(n):
                name = random.choice(member_list)
                if i == n-1:
                    content += name
                else:
                    content += name+'\n'
                member_list.remove(name)
        except:
            content = '無法在此處抽選'
        text_reply(content)

    if '.jpg' in get_message.lower() or '.png' in get_message.lower():
        if split[-1].isdigit():
            n = int(split[-1])
            if(n > 10):
                n = 10
        else:
            n = 1
        URL_list = []
        params = {
            "engine": "google",
            "tbm": "isch"
        }
        try:
            params['q'] = get_message[:-2]
            params['api_key'] = random.choice(jdata['serpapi_key'])
            client = GoogleSearch(params)
            data = client.get_dict()
            while('error' in data.keys()):
                params['api_key'] = random.choice(jdata['serpapi_key'])
                client = GoogleSearch(params)
                data = client.get_dict()
            imgs = data['images_results']
            x = 0
            if(n > len(imgs)):
                n = len(imgs)
            for img in imgs:
                if x < n and img['original'][-4:].lower() in ['.jpg', '.png', 'jpeg'] and img['original'][:5] == 'https':
                    URL_list.append(img['original'])
                    x += 1
            with open('json/imgBubble.json', 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
            ctn = []
            for i in range(n):
                tmp = copy.deepcopy(jdata)
                tmp['hero']['url'] = tmp['hero']['action']['uri'] = URL_list[i]
                ctn.append(tmp)

            if len(ctn) > 1:
                with open('json/carousel.json', 'r', encoding='utf8') as jfile:
                    jdataCtn = json.load(jfile)
                jdataCtn['contents'] = ctn
                reply = jdataCtn
                line_bot_api.reply_message(
                    event.reply_token, FlexSendMessage('imgs', reply))
            else:
                img_reply(ctn[0]['hero']['url'])
        except:
            url = 'https://www.google.com.tw/search?q=' + get_message + '&tbm=isch'
            request = requests.get(url=url)
            html = request.content
            bsObj = BeautifulSoup(html, 'html.parser')
            content = bsObj.findAll('img', {'class': 't0fcAb'})
            for i in content:
                URL_list.append(i['src'])
            url = random.choice(URL_list)
            img_reply(url)

    if get_message[:3].lower() == '!yt':
        if split[-1].isdigit():
            x = int(split[-1])
            s = 1
        else:
            x = 3
            s = 0
        URL = ''
        YOUTUBE_API_KEY = jdata['YOUTUBE_API_KEY']
        if s == 1:
            q = get_message[4:-2]
        else:
            q = get_message[4:]
        url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q=' + \
            q+'&key='+YOUTUBE_API_KEY+'&type=video&maxResults='+str(x)
        request = requests.get(url)
        data = request.json()
        for i in range(x):
            URL += 'https://www.youtube.com/watch?v=' + \
                data['items'][i]['id']['videoId']+'\n'
        text_reply(URL)

    if get_message[:2].lower() == '!s' or get_message[:4] == '有人知道' or (get_message[:1] == '教' and get_message[-1:] == '嗎' and len(get_message) > 2):
        text = ''
        if get_message[:2].lower() == '!s':
            query = get_message[2:]
        elif get_message[:4] == '有人知道':
            query = get_message[4:-1]
        elif get_message[:1] == '教' and get_message[-1:] == '嗎':
            query = get_message[1:-1]
        for url in search(query, stop=3):
            if url not in text:
                text += url+'\n\n'
        text_reply(text)

    if get_message[:26] == 'https://www.instagram.com/':
        pass

    if split[0] == '!tmr':
        data = {
            'idpwLgid': os.environ.get("SMA_ID"),
            'idpwLgpw': os.environ.get("SMA_PW"),
            'my_prevtyp': 'S',
            'my_prevdom': 'smavoice.jp',
            'my_prevurl': '/s/sma03/artist/45/contents',
            'my_prevmet': 'GET',
            'my_webckid': '79666726243d1f7e073d7d3b90e48ebd6da66176',
            'my_prevprm': '{"ct":"45_122_02","tp":"122","arti":"45","cd":"45"}',
            'mode': 'LOGIN',
            'ima': 3340

        }
        url = 'https://smavoice.jp/s/sma03/login'
        session = requests.Session()
        session.post(url, headers=send_headers, data=data)
        URL = []
        # 登入後，我們需要獲取另一個網頁中的內容
        response = session.get(
            'https://smavoice.jp/s/sma03/artist/45/contents?ima=4940&ct=45_122_02&tp=122&arti=45', headers=send_headers)
        html = response.content
        bsObj = BeautifulSoup(html, 'html.parser')
        shouter = bsObj.findAll('img', {'class': 'nocover'})
        try:
            limit = int(split[1])
        except:
            limit = 10000
        count = 0
        for i in shouter:
            if count == limit:
                break
            URL.append('https://smavoice.jp'+i['src'])
            count += 1
        if(split[1].isdigit()):
            text = ''
            for i in URL:
                text += i+'\n'
            text_reply(text)
        else:
            index = int(split[1][1:])
            if index > len(URL):
                index = len(URL)
            text_reply(URL[index-1])

    if get_message[:3].lower() == '!nh':
        content = ''
        URL = 'https://nhentai.net'
        serach_URL = 'https://nhentai.net/search/?q='
        if get_message.lower() == '!nh':
            q = 'a'
            serach_URL += q
            request = requests.get(serach_URL)
            html = request.content
            bsObj = BeautifulSoup(html, 'html.parser')
            shouter = bsObj.findAll('a', {'class': 'cover'})
            for i in shouter:
                num = i['href'][3:-1]
                break
            num = random.randint(1, int(num)+1)
            content = URL + '/g/' + str(num) + '/'
        elif split[-1].isdigit() and len(split) == 2:
            num = int(get_message[4:])
            content = URL + '/g/' + str(num) + '/'
        else:
            if split[-1].isdigit():
                q = get_message[4:-1*(len(split[-1])+1)]
                n = int(split[-1])
            else:
                q = get_message[4:]
                n = 5
            serach_URL += q
            request = requests.get(serach_URL)
            html = request.content
            bsObj = BeautifulSoup(html, 'html.parser')
            shouter = bsObj.findAll('a', {'class': 'cover'})
            t = 0
            for i in shouter:
                t += 1
                if t == n+1:
                    break
                else:
                    content += URL+i['href']
                    if t != n:
                        content += '\n'
        text_reply(content)

    if get_message == '!戴男':
        rand_voice = random.choice(jdata['dai_voice'])
        audio_reply(rand_voice)

    if get_message[:5] == '!echo':
        text_reply(get_message[6:])

    elif get_message[:4] != 'http':

        if '機器人' in get_message or 'bot' in get_message:
            for i in jdata['abuse_words']:
                if i in get_message:
                    text_reply(user_name+'兇三小 家裡死人喔 = =')
            for i in jdata['praise_words']:
                if i in get_message:
                    img_reply(
                        'https://cdn.discordapp.com/attachments/856516846144192543/863114640345923604/image0.png')

        if get_message == '笑死':
            randNum = random.randint(1, 10)
            if randNum == 1:
                text_reply('死了沒')
            elif randNum == 2:
                text_reply('好好笑喔好好笑喔')
            else:
                text_reply('')

        for i in jdata['echo_words']:
            if i in get_message:
                if get_message[0] == '我':
                    get_message = get_message.replace('我', '你')
                if "不會" not in get_message:
                    get_message = get_message.replace('會', '才會')
                if "會不會" not in get_message:
                    get_message = get_message.replace('會不會', '才會')
                if "你是" in get_message or "妳是" in get_message:
                    get_message = get_message.replace('是', '才是')
                    get_message = get_message.replace('才是不才是', '才是')
                text_reply(get_message)
                break
        for i in jdata['china_words']:
            if i in get_message:
                random_pic = random.choice(jdata['chPolice_pic'])
                img_reply(random_pic)
                break
        for i in jdata['full_echo_words']:
            if i == get_message:
                text_reply(get_message)
                break

        if '買' in get_message:
            if '會員' in get_message:
                text_reply('買 我叫你買')

        if '我' in get_message:
            if '不會' in get_message and len(get_message) < 20:
                text_reply('哈哈你又不會了')

        if '教嗎' in get_message or '教嘛' in get_message or '教？' in get_message or '教?' in get_message:
            text_reply('不要嘲諷好嗎')

        if '加推' in get_message or '我婆' in get_message:
            text_reply('又？')

        if '一生' in get_message and '推' in get_message and '不' not in get_message:
            text_reply(user_name+'你真可憐')

    if l_get_message[:17] == 'https://youtu.be/' or l_get_message[:24] == 'https://www.youtube.com/' or l_get_message[:22] == "https://m.youtube.com/":
        YOUTUBE_API_KEY = jdata['YOUTUBE_API_KEY']
        if l_get_message[:17] == 'https://youtu.be/':
            id = l_get_message[17:].rstrip()
        elif l_get_message[:24] == 'https://www.youtube.com/':
            id = l_get_message[32:].rstrip()
        elif l_get_message[:22] == "https://m.youtube.com/":
            id = l_get_message[30:].rstrip()
        URL = 'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=' + \
            id+'&key='+YOUTUBE_API_KEY
        request = requests.get(URL)
        data = request.json()
        title = data['items'][0]['snippet']['title']
        channel = data['items'][0]['snippet']['channelTitle']
        view = data['items'][0]['statistics']['viewCount']
        try:
            like = data['items'][0]['statistics']['likeCount']
        except:
            like = 'N/A'
        try:
            dislike = data['items'][0]['statistics']['dislikeCount']
        except:
            dislike = 'N/A'
        try:
            comment = data['items'][0]['statistics']['commentCount']
        except:
            comment = 'N/A'
        channelId = data['items'][0]['snippet']['channelId']
        URL2 = 'https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + \
            channelId+'&key='+YOUTUBE_API_KEY
        request = requests.get(URL2)
        data = request.json()
        try:
            sub = data['items'][0]['statistics']['subscriberCount']
        except:
            sub = 'N/A'
        text = title+'\n' +\
            '-'+'\n' +\
            '<頻道資訊>\n' +\
            channel+'\n' +\
            '訂閱數: '+str(sub)+'\n'\
            '-'+'\n' +\
            '<影片資訊>\n' +\
            '觀看數: '+str(view)+'\n' +\
            '讚數: '+str(like)+'    倒讚數: '+str(dislike)+'\n' +\
            '留言數: '+str(comment)+'\n'
        text_reply(text)

    if 'ptt' in get_message and '不印出' not in get_message:
        start = get_message.find('http')
        end = get_message.find('.html')
        URL = get_message[start:end+5]
        payload = {
            'from': '/bbs/Gossiping/index.html',
            'yes': 'yes'
        }
        rs = requests.session()
        request = rs.post('https://www.ptt.cc/ask/over18', data=payload)
        request = rs.get(URL)
        html = request.text
        bsObj = BeautifulSoup(html, 'html.parser')
        shouter = bsObj.findAll('span', 'article-meta-value')
        author = shouter[0].text
        title = shouter[2].text
        main_container = bsObj.find(id='main-container')
        all_text = main_container.text
        print(all_text)
        if '留言' in get_message:
            pre_comment = all_text.split('批踢踢實業坊(ptt.cc)')[1]
            pre_comment_list = pre_comment.split('html')[1:]
            pre_comment = ''.join(pre_comment_list)
            pre_comment_list = pre_comment.split('\n')
            text = '\n\n'.join(pre_comment_list)
        else:
            pre_text = all_text.split('批踢踢實業坊(ptt.cc)')[0]
            pre_text_list = pre_text.split('--')[:-1]
            pre_text = ''.join(pre_text_list)
            texts = pre_text.split('\n')
            contents = texts[2:]
            content = '\n'.join(contents)
            text = title + '\n' +\
                '作者: '+author + '\n' +\
                '-'+'\n' +\
                content
        if len(text) > 5000:
            text = text[:5000]
        text_reply(text)

    if 'twitter.com' in get_message:
        urlElement = get_message.split('/')
        auth = tweepy.OAuthHandler(os.environ.get(
            "TWITTER_APP_KEY"), os.environ.get("TWITTER_APP_SECRET"))
        auth.set_access_token(os.environ.get(
            "TWITTER_ACCESS_TOKEN"), os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"))
        api = tweepy.API(auth)

        try:
            tweet = api.get_status(urlElement[-1], tweet_mode="extended")
            url = tweet.extended_entities["media"][0]["video_info"]["variants"][0]["url"].split('?')[
                0]
            url2 = tweet.extended_entities["media"][0]['media_url']
            if('https' not in url2):
                url2 = url2.replace('http', 'https')
            video_reply(url, url2)
        except:
            tweet = api.get_status(urlElement[-1])
            with open('json/twitterBubble.json', 'r', encoding='utf8') as jfile:
                jdata1 = json.load(jfile)
            with open('json/imgBubble.json', 'r', encoding='utf8') as jfile:
                jdata2 = json.load(jfile)
            ctn = []
            jdata1['body']['contents'][0]['url'] = tweet.user.profile_image_url.replace(
                'http', 'https')
            jdata1['body']['contents'][1]['text'] = tweet.user.name
            jdata1['body']['contents'][2]['text'] = '@'+tweet.user.screen_name
            jdata1['body']['contents'][3]['contents'][1]['text'] = str(
                tweet.user.followers_count)
            jdata1['body']['contents'][5]['contents'][0]['text'] = tweet.text
            jdata1['body']['contents'][5]['contents'][2]['contents'][1]['text'] = str(
                tweet.retweet_count)
            jdata1['body']['contents'][5]['contents'][3]['contents'][1]['text'] = str(
                tweet.favorite_count)
            ctn.append(jdata1)
            tweet = api.get_status(urlElement[-1], tweet_mode="extended")
            if 'media' in tweet.entities:
                for media in tweet.extended_entities['media']:
                    tmp = copy.deepcopy(jdata2)
                    if('https' not in media['media_url']):
                        tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url'].replace(
                            'http', 'https')
                    else:
                        tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url']
                    ctn.append(tmp)
            if len(ctn) > 1:
                with open('json/carousel.json', 'r', encoding='utf8') as jfile:
                    jdataCtn = json.load(jfile)
                jdataCtn['contents'] = ctn
                reply = jdataCtn
            else:
                reply = jdata1
            line_bot_api.reply_message(
                event.reply_token, FlexSendMessage('tweet', reply))

    if 'forum.gamer.com.tw' in get_message:
        # cookie = eval(jdata['baha_cookie'])
        # request = requests.get(l_get_message, headers=cookie)
        # html = request.content
        # print(html)
        # bsObj = BeautifulSoup(html, 'html.parser')
        # shouter = bsObj.find('h1', {'class', 'c-post__header__title'})
        # title = shouter.text
        # shouter = bsObj.find('a', {'class', 'username'})
        # poster = shouter.text
        # shouter = bsObj.findAll('a', {'class', 'tippy-gpbp-list'})
        # x = 0
        # for item in shouter:
        #     if x == 0:
        #         GP = item.text
        #     elif x == 1:
        #         BP = item.text
        #     else:
        #         break
        #     x += 1
        # content = ''
        # shouter = bsObj.findAll('div', {'class', 'c-article__content'})
        # for item in shouter:
        #     shouter2 = item.findAll('div')
        #     for item2 in shouter2:
        #         content += item2.text+'\n'
        #     break
        # if len(content) > 1000:
        #     content = content[:1000]
        #     content += '\n\n-字數過多,以下省略-'
        # text = title+'\n' +\
        #     '樓主: '+poster+'\n' +\
        #     'GP: '+GP+'  BP: '+BP+'\n' +\
        #     '- \n' +\
        #     content
        # text_reply(text)
        pass

    if get_message[:5] == '!rand':
        content = list(map(int, get_message[6:].split()))
        if len(get_message[6:].split()) == 1:
            min = 0
            max = content[0]
            num = random.randint(min, max+1)
        else:
            num = ''
            choosed_list = []
            min = content[0]
            max = content[1]
            if len(get_message[6:].split()) == 2:
                times = 1
            elif len(get_message[6:].split()) == 3:
                times = content[2]
                if times > max - min:
                    times = max - min
                elif times > 5000:
                    times = 5000
            for i in range(times):
                rand = random.randint(min, max)
                while rand in choosed_list:
                    rand = random.randint(min, max)
                choosed_list.append(rand)
                num += str(rand)
                if i != times-1:
                    num += '\n'
        text_reply(num)

    if get_message[:5] == '!rate':
        money = get_message[6:]
        money = money.lower()
        data = ['usd', 'hkd', 'gbp', 'aud', 'cad', 'sgd', 'chf', 'jpy', 'zar',
                'sek', 'nzd', 'thb', 'php', 'idr', 'eur', 'krw', 'vnd', 'myr', 'cny']
        num = data.index(money)
        URL = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'
        request = requests.get(URL, headers=send_headers)
        html = request.content
        bsObj = BeautifulSoup(html, 'html.parser')
        rate_table = bsObj.find('table', attrs={'title': '牌告匯率'}).find(
            'tbody').find_all('tr')
        buyin_rate = rate_table[num].find(
            'td', attrs={'data-table': '本行即期買入'})
        sellout_rate = rate_table[num].find(
            'td', attrs={'data-table': '本行即期賣出'})
        words = money.upper()+"\n即時即期買入: {}\n即時即期賣出: {}".format(buyin_rate.get_text().strip(),
                                                                sellout_rate.get_text().strip())
        text_reply(words)

    if get_message[:5] == '!vote':
        FlexMessage = json.load(open('json/vote.json', 'r', encoding='utf-8'))
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage('profile', FlexMessage))

    if get_message == '!history':
        CLIENT_ID = "14dcbae49ad6b84"
        sheet = sheet_reload("1ti_4scE5PyIzcH4s6mzaWaGqiIQfK9X_R--oDXqyJsA")
        data = sheet.get_all_values()
        dates = [data[i][0]for i in range(len(data))]
        times = [data[i][1]for i in range(len(data))]
        t = 0
        X = []
        Y = []
        for i in range(1, 15):
            if(t == 7):
                break
            if(dates[-i] in X):
                Y[len(Y)-1] += times[-i]
            else:
                X.append(dates[-i][5:])
                Y.append(int(times[-i]))
                t += 1
        X.reverse()
        Y.reverse()
        plt.plot(X, Y)
        plt.title("Message Counting(only text)")
        for a, b in zip(X, Y):
            plt.text(a, b, b, ha='center', va='bottom', fontsize=12)
        plt.savefig("test.jpg")
        PATH = "test.jpg"  # A Filepath to an image on your computer"
        title = "Uploaded with PyImgur"
        im = pyimgur.Imgur(CLIENT_ID)
        uploaded_image = im.upload_image(PATH, title=title)
        os.remove("test.jpg")
        img_reply(uploaded_image.link)

    if l_get_message == '!bot':
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TemplateSendMessage(
                alt_text='Buttons template',
                template=ButtonsTemplate(
                    title='遊戲選單',
                    text='請選擇遊戲',
                    actions=[
                        MessageTemplateAction(
                            label='game1',
                            text='game1',
                            data='A&game1'
                        ),
                        MessageTemplateAction(
                            label='game2',
                            text='game2',
                            data='A&game2'
                        ),
                        MessageTemplateAction(
                            label='game3',
                            text='Upcoming...',
                            data='A&game3'
                        )
                    ]
                )
            )
        )

    if Message_container[0] == Message_container[1] and Message_container[0] == Message_container[2]:
        text = Message_container[0]
        if Message_send != text:
            Message_send = text
            text_reply(text)

    sheet, bully_names, bully_p, bully_words = bully_reload()

    if user_name in bully_names:
        p = bully_p[bully_names.index(user_name)]
        words = bully_words[bully_names.index(user_name)]
        bully(int(p), words)


@handler.add(PostbackEvent)  # Postback的部分
def handle_postback(event):
    data = event.postback.data
