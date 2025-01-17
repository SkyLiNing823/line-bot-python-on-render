import os
from datetime import datetime
import json
import copy
import os
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
# import tweepy
import pyimgur
import matplotlib.pyplot as plt
import speech_recognition as sr
from pydub import AudioSegment
import gtts
import cv2
import numpy as np
# from imageai.Detection import ObjectDetection
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from saucenao_api import SauceNao
import pyscord_storage
import websocket
import base64
import audioread
import pprint
import google.generativeai as palm

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


from flask import Flask, abort, request


def line_reply(reply, event):
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(event.reply_token, reply)


def text_reply(content, event):
    reply = TextSendMessage(text=content)
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(event.reply_token, reply)


def rand_text_reply(n, content, event):
    randNum = random.randint(1, n)
    if randNum == 1:
        text_reply(content, event)


def img_reply(URL, event):
    reply = ImageSendMessage(
        original_content_url=URL, preview_image_url=URL)
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(event.reply_token, reply)


def audio_reply(URL, duration, event):
    reply = AudioSendMessage(
        original_content_url=URL, duration=duration)
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(event.reply_token, reply)


def video_reply(URL, URL2, event):
    reply = VideoSendMessage(
        original_content_url=URL, preview_image_url=URL2)
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(event.reply_token, reply)


def flex_reply(words, content, event):
    reply = FlexSendMessage(words, content)
    LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
               ).reply_message(
        event.reply_token, reply)


def img_save(url, event):
    try:
        id = event.source.group_id
    except:
        id = event.source.user_id
    PATH = f'{id}.png'
    response = requests.get(url)
    with open(PATH, "wb") as f:
        f.write(response.content)


def F_sound2text(event):
    PATH = 'tmp.mp3'
    audio_content = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
                               ).get_message_content(event.message.id)
    with open(PATH, 'wb') as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)
    fd.close()
    # 轉檔
    dst = PATH.replace("mp3", "wav")
    sound = AudioSegment.from_file(PATH)
    sound.export(dst, format="wav")
    # 辨識
    r = sr.Recognizer()
    with sr.AudioFile(dst) as source:
        audio = r.record(source)
    text = r.recognize_google(audio, language='zh-Hant')
    os.remove("tmp.wav")
    text_reply(text, event)


def sheet_reload(key):
    scopes = ["https://spreadsheets.google.com/feeds"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "json/credentials.json", scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(key).sheet1
    return sheet


def uploadIMG(PATH):
    CLIENT_ID = "14dcbae49ad6b84"
    title = "Uploaded with PyImgur"
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=title)
    return uploaded_image.link


def F_history(event):
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
    plt.savefig("tmp.jpg")
    PATH = "tmp.jpg"
    link = uploadIMG(PATH)
    os.remove("tmp.jpg")
    img_reply(link, event)


def F_countMSG(event):
    sheet = sheet_reload("1ti_4scE5PyIzcH4s6mzaWaGqiIQfK9X_R--oDXqyJsA")
    data = sheet.get_all_values()
    dates = [data[i][0]for i in range(len(data))]
    times = [data[i][1]for i in range(len(data))]
    dt = (datetime.datetime.today() +
          datetime.timedelta(hours=8)).strftime("%Y/%m/%d")
    if dt not in dates:
        F_history(event)
        sheet.append_row([dt, '1'])
    else:
        n = int(times[dates.index(dt)])
        sheet.update_cell(dates.index(dt)+1, 2, str(n+1))


def resp_reload():
    sheet = sheet_reload("1GmO4ygrYvr2fv7z-PuFZZegQDt694PyMidHL3KWEHU4")
    respData = sheet.get_all_values()
    resp_names = [respData[i][0]
                   for i in range(len(respData))]
    resp_p = [respData[i][1]
               for i in range(len(respData))]
    words = [respData[i][2]
             for i in range(len(respData))]
    resp_words = []
    for i in words:
        resp_words.append(i.split(','))
    return sheet, resp_names, resp_p, resp_words


def resp(n, List, event):
    if n > 0:
        randNum = random.randint(1, n)
        if randNum == 1:
            text = random.choice(List)
            text_reply(text, event)


def F_respManager(split, event):
    sheet, resp_names, resp_p, resp_words = resp_reload()
    if len(split) == 2:
        if split[1] == 'list':
            keys = ""
            for i in range(len(resp_names)):
                if int(resp_p[i]) != 0:
                    keys += resp_names[i]+'\n'
            text_reply(f'名單:\n{keys}', event)
        elif split[1] in resp_names:
            p = resp_p[resp_names.index(split[1])]
            words = resp_words[resp_names.index(split[1])]
            text_reply(f'p:{p}\nwords:\n{words}', event)
        else:
            text_reply(f'名單無此人', event)
    elif split[2] == 'p':
        if split[1] in resp_names:
            resp_p[resp_names.index(split[1])] = split[3]
            sheet.update_cell(resp_names.index(
                split[1])+1, 2, split[3])
            text_reply(f'{split[1]}的回覆機率已調整為1/{split[3]}', event)
        else:
            sheet.append_row([split[1], split[3], f'{split[1]}你好'])
            text_reply(f'{split[1]}未登錄回覆名單，現已登錄且將被回覆機率設為1/{split[3]}', event)
    elif split[2] == '+':
        if split[1] in resp_names:
            if split[3] not in resp_words[resp_names.index(split[1])]:
                resp_words[resp_names.index(
                    split[1])].append(split[3])
                words = ''
                for i in resp_words[resp_names.index(split[1])]:
                    words += ','+str(i)
                sheet.update_cell(
                    resp_names.index(split[1])+1, 3, words[1:])
                text_reply(
                    f'資料庫已加入「{split[3]}」\n現已收錄:{resp_words[resp_names.index(split[1])]}', event)
            else:
                text_reply('此句已存在', event)
        else:
            sheet.append_row([split[1], '5', split[3]])
            text_reply(f'{split[1]}未登錄回覆名單\n現已登錄且收錄:[\'{split[3]}\']', event)
    elif split[2] == '-':
        if split[1] in resp_names:
            if split[3] in resp_words[resp_names.index(split[1])]:
                resp_words[resp_names.index(
                    split[1])].remove(split[3])
                words = ''
                for i in resp_words[resp_names.index(split[1])]:
                    words += ','+str(i)
                sheet.update_cell(
                    resp_names.index(split[1])+1, 3, words[1:])

                text_reply(
                    f'資料庫已刪除「{split[3]}」\n現已收錄:{resp_words[resp_names.index(split[1])]}', event)
            else:
                text_reply('此句不存在', event)
        else:
            text_reply(f'{split[1]}未登錄回覆名單', event)
    elif split[2] == 'del':
        if split[1] in resp_names:
            resp_p[resp_names.index(split[1])] = '0'
            sheet.update_cell(resp_names.index(
                split[1])+1, 2, '0')
            keys = ""
            for i in range(len(resp_names)):
                if int(resp_p[i]) != 0:
                    keys += resp_names[i]+'\n'
            text_reply(f'成員已移除{split[1]}\n目前名單:\n{keys}', event)
        else:
            text_reply(f'成員名單不存在{split[1]}', event)


def F_translate(get_message, split, event):
    translator = googletrans.Translator()
    text = get_message[3:]
    if text == '?':
        trans = str(googletrans.LANGCODES)[1:-1].replace(', ', '\n')
    elif split[1] in googletrans.LANGCODES.values() and len(split) != 2:
        text = get_message[6:]
        trans = translator.translate(text, dest=split[1]).text
    else:
        trans = translator.translate(text, dest='zh-tw').text
    text_reply(trans, event)


def F_TTS(get_message, event):
    VoiceDict = {'mika': 65, 'ミカ': 65,
                 'miyu': 70, 'ミユ': 70,
                 'karin': 75, 'カリン': 75,
                 'asuna': 80, 'アスナ': 80,
                 'azusa': 85, 'アズサ': 85,
                 'alice': 90, 'アリス': 90,
                 'shiroko': 95, 'シロコ': 95,
                 'hoshino': 100, 'ホシノ': 100,
                 'hina': 105, 'ヒナ': 105,
                 'iori': 110, 'イオリ': 110,
                 'izuna': 115, 'イズナ': 115,
                 'yuuka': 120, 'ユウカ': 120}
    if get_message.split()[1] in ['?', '？']:
        text_reply(str(gtts.lang.tts_langs()), event)
        return
    elif get_message.split()[1].lower() in VoiceDict.keys():
        uri = 'wss://vocal.dvd.moe/queue/join'
        ws = websocket.create_connection(uri, timeout=10)
        LAN = 'Japanese'
        message1 = {"session_hash": "iohm2xkgjq", "fn_index": 0}
        message2 = {"fn_index": VoiceDict[get_message.split()[1].lower()], "data": [get_message[len(get_message.split(
        )[0])+len(get_message.split()[1])+2:], LAN, 0.6, 0.668, 1, False], "session_hash": "iohm2xkgjq"}
        message1 = json.dumps(message1)
        message2 = json.dumps(message2)
        ws.send(message1)
        ws.send(message2)
        while True:
            result = ws.recv()
            results = json.loads(result)
            if 'Success' in result:
                break
        data = results['output']['data'][1].split(',')[1]
        decoded_data = base64.b64decode(data)
        with open('tmp.wav', 'wb') as f:
            f.write(decoded_data)

    elif get_message.split()[1].lower() in list(gtts.lang.tts_langs().keys()) and len(get_message.split()) > 2:
        LAN = get_message.split()[1].lower()
        tts = gtts.gTTS(text=get_message[8:], lang=LAN)
        tts.save("tmp.wav")
    else:
        LAN = 'zh-tw'
        tts = gtts.gTTS(text=get_message[5:], lang=LAN)
        tts.save("tmp.wav")
    with audioread.audio_open('tmp.wav') as f:
        duration = int(f.duration) * 1000
    data = pyscord_storage.upload('tmp.wav', 'tmp.wav')['data']
    URL = data['url']
    # print(data['url'])
    audio_reply(URL, duration, event)


def F_eval(get_message, event):
    operator = ['+', '-', '*', '/', '%', '.', '(', ')', ' ']
    test = get_message
    for i in operator:
        test = test.replace(i, '')
    if test.isdigit() and get_message.isdigit() == False:
        content = str(round(eval(get_message), 4))
        text_reply(content, event)
    else:
        return


def F_lottery(jdata, group_id, split, event):
    if group_id == "C0862e003396d3da93b9016d848560f29":
        sheet = sheet_reload("1EfgW0_aNkc_r790Htp3NTmhSRfHuriil1u0YZhPYrAo")
        memberData = sheet.get_all_values()
        member_list = [memberData[i][0]
                       for i in range(len(memberData))]
        if len(split) == 1:
            name = random.choice(member_list)
            text_reply(f'{name}', event)
        elif len(split) == 2 and split[1].isdigit():
            content = ''
            if int(split[1]) > len(member_list):
                split[1] = len(member_list)
            for i in range(int(split[1])):
                name = random.choice(member_list)
                if i == int(split[1])-1:
                    content += name
                else:
                    content += name+'\n'
                member_list.remove(name)
            text_reply(content, event)
        elif split[1] == 'list':
            content = ''
            for i in range(len(member_list)):
                if i == len(member_list)-1:
                    content += member_list[i]
                else:
                    content += member_list[i]+'\n'
            text_reply(content, event)
        elif split[1] == '+':
            if split[2] not in member_list:
                sheet.append_row([split[2]])
                member_list.append(split[2])
                text_reply(f'已將{split[2]}登錄成員名單', event)
            else:
                text_reply(f'{split[2]}已在成員名單', event)
        elif split[1] == '-':
            if split[2] not in member_list:
                text_reply(f'成員名單不存在{split[2]}', event)
            else:
                member_list.remove(split[2])
                for i in range(len(member_list)):
                    sheet.update_cell(i+1, 1, member_list[i])
                sheet.update_cell(len(member_list)+1, 1, '')
                text_reply(f'已將{split[2]}於成員名單刪除', event)
    else:
        text_reply('不可於此處抽選', event)


def F_imgSearch(split, jdata, get_message, event):
    if split[-1].isdigit():
        n = int(split[-1])
        get_message = get_message[:-len(split[-1])]
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
        params['q'] = get_message[:-4]
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
        img_save(URL_list[-1], event)
        for i in range(n):
            tmp = copy.deepcopy(jdata)
            tmp['hero']['url'] = tmp['hero']['action']['uri'] = URL_list[i]
            ctn.append(tmp)
        if len(ctn) > 1:
            with open('json/carousel.json', 'r', encoding='utf8') as jfile:
                jdataCtn = json.load(jfile)
            jdataCtn['contents'] = ctn
            reply = jdataCtn
            flex_reply('imgs', reply, event)
        else:
            img_reply(ctn[0]['hero']['url'], event)
    except:
        url = 'https://www.google.com.tw/search?q=' + get_message + '&tbm=isch'
        request = requests.get(url=url)
        html = request.content
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.findAll('img', {'class': 't0fcAb'})
        for i in content:
            URL_list.append(i['src'])
        url = random.choice(URL_list)
        img_reply(url, event)


def F_ytSearch(split, get_message, jdata, event):
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
    text_reply(URL, event)


def F_GoogleSearch(get_message, event):
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
    text_reply(text, event)


def F_tmr(send_headers, split, event):
    data = {
        'idpwLgid': os.getenv('SMA_ID', None),
        'idpwLgpw': os.getenv('SMA_PW', None),
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
        text_reply(text, event)
    else:
        index = int(split[1][1:])
        if index > len(URL):
            index = len(URL)
        text_reply(URL[index-1], event)


def F_ytPreview(l_get_message, jdata, event):
    YOUTUBE_API_KEY = jdata['YOUTUBE_API_KEY']
    if l_get_message[:17] == 'https://youtu.be/':
        id = l_get_message[17:l_get_message.index('?')].rstrip()
    elif l_get_message[:24] == 'https://www.youtube.com/':
        id = l_get_message[32:l_get_message.index('?')].rstrip()
    elif l_get_message[:22] == "https://m.youtube.com/":
        id = l_get_message[30:l_get_message.index('?')].rstrip()
    print(id)
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
    text = title+'\n' + \
        '-'+'\n' +\
        '<頻道資訊>\n' +\
        channel+'\n' +\
        '訂閱數: '+str(sub)+'\n'
    '-'+'\n' +\
        '<影片資訊>\n' +\
        '觀看數: '+str(view)+'\n' +\
        '讚數: '+str(like)+'    倒讚數: '+str(dislike)+'\n' +\
        '留言數: '+str(comment)+'\n'
    text_reply(text, event)


def F_pttPreview(get_message, event):
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
    if '留言' in get_message:
        pre_comment = all_text.split('批踢踢實業坊(ptt.cc)')[1]
        pre_comment_list = pre_comment.split('html')[1:]
        pre_comment = ''.join(pre_comment_list)
        pre_comment_list = pre_comment.split('\n')
        text = '\n\n'.join(pre_comment_list)
    else:
        pre_text = all_text.split('批踢踢實業坊(ptt.cc)')[0]
        pre_text = pre_text.split('\n--\n')[0]
        texts = pre_text.split('\n')
        contents = texts[2:]
        content = '\n'.join(contents)
        text = title + '\n' + '作者: '+author + '\n' + '-'+'\n' + content
    if len(text) > 5000:
        text = text[:5000]
    text_reply(text, event)


def F_twitterPreview(get_message, event):
    stack = []
    msg = []
    ctn = []
    with open('twitterStack.txt', 'a') as f:
        f.write(get_message+'\n')
    with open('twitterStack.txt', 'r') as f:
        for line in f.readlines():
            stack.append(line)
    for link in stack:
        url = 'https://tweetpik.com/api/v2/tweets?url='+link
        request = requests.get(url)
        contents = request.text
        if "avatarUrl" in contents:
            username = contents[contents.find(
                '<span class=\\"css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0\\"><span class=\\"css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0\\">')+len('<span class=\\"css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0\\"><span class=\\"css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0\\">'):contents.find('</span>')]
            screen_name = contents[contents.find(
                '"handler":"')+len('"handler":"'):contents.find('","avatarUrl":"')]
            if '.jpg' in contents:
                profile_image_url = contents[contents.find(
                    '","avatarUrl":"')+len('","avatarUrl":"'):contents.find('.jpg')+4]
            else:
                profile_image_url = contents[contents.find(
                    '","avatarUrl":"')+len('","avatarUrl":"'):contents.find('.png')+4]
            if 'https' not in profile_image_url:
                profile_image_url = 'https://upload.wikimedia.org/wikipedia/commons/5/50/Black_colour.jpg'
            if 'textHtml' in contents:
                tweet_text_HTML = contents[contents.find(
                    '"textHtml":"')+len('"textHtml":"'):contents.find('","verified"')]
                bsObj = BeautifulSoup(tweet_text_HTML, 'html.parser')
                tweet_text = ''
                for i in bsObj:
                    tweet_text += i.text
                tweet_text = tweet_text.replace('\\n', '\n')
            else:
                tweet_text = ' '
            retweet_count = str(contents[contents.find(
                '"retweets":')+len('"retweets":'):contents.find(',"replies"')])
            if retweet_count == 'null':
                retweet_count = '0'
            favorite_count = str(contents[contents.find(
                ',"likes":')+len(',"likes":'):contents.find(',"retweets":')])
            if favorite_count == 'null':
                favorite_count = '0'
            with open('json/twitterBubble.json', 'r', encoding='utf8') as jfile:
                jdata1 = json.load(jfile)
            jdata1['body']['contents'][0]['url'] = profile_image_url
            jdata1['body']['contents'][1]['text'] = username
            jdata1['body']['contents'][2]['text'] = screen_name
            jdata1['body']['contents'][4]['contents'][0]['text'] = tweet_text
            jdata1['body']['contents'][4]['contents'][2]['contents'][1]['text'] = retweet_count
            jdata1['body']['contents'][4]['contents'][3]['contents'][1]['text'] = favorite_count
            photos_urls = contents[contents.find(
                '"photos":[')+len('"photos":['):contents.find('],"videos"')].split(',')
            msg.append(FlexSendMessage('tweet', jdata1))
            if photos_urls[0] != '':
                with open('json/imgBubble.json', 'r', encoding='utf8') as jfile:
                    jdata2 = json.load(jfile)
                for i in range(len(photos_urls)):
                    tmp = copy.deepcopy(jdata2)
                    if 'jpg' in photos_urls[i]:
                        img_url = photos_urls[i][1:photos_urls[i].find(
                            '?')]+'.jpg'
                    else:
                        img_url = photos_urls[i][1:photos_urls[i].find(
                            '?')]+'.png'
                    print(img_url)
                    if 'https' in img_url:
                        tmp['hero']['url'] = tmp['hero']['action']['uri'] = img_url
                        ctn.append(tmp)
                        url = img_url
                img_save(url, event)
                if len(ctn) > 1:
                    with open('json/carousel.json', 'r', encoding='utf8') as jfile:
                        jdata = json.load(jfile)
                    jdata['contents'] = ctn
                    reply = jdata
                    msg.append(FlexSendMessage('tweet', reply))
                elif len(ctn) == 1:
                    msg.append(ImageSendMessage(
                        original_content_url=img_url, preview_image_url=img_url))
            else:
                p = {'url': get_message}
                r = requests.post(
                    'https://www.expertsphp.com/instagram-reels-downloader.php', data=p)
                html = r.content
                bsObj = BeautifulSoup(html, 'html.parser')
                if 'mp4' in r.text:
                    videos = bsObj.findAll(
                        'a', {'class': 'btn-sm'})
                    max_resolution = 0
                    for video in videos:
                        if 'mp4' in video['href']:
                            resolution = eval(video['href'].split(
                                '/')[-2].replace('x', '*'))
                            if resolution > max_resolution:
                                video_url = video['href']
                                max_resolution = resolution
                        else:
                            img_url = video['href']
                    msg.append(VideoSendMessage(
                        original_content_url=video_url, preview_image_url=img_url))
                else:
                    imgs = bsObj.findAll('img', {'alt': 'Thumbnail'})
                    for img in imgs:
                        img_url = img['src']
                    msg.append(ImageSendMessage(
                        original_content_url=img_url, preview_image_url=img_url))
        else:
            p = {'url': get_message}
            r = requests.post(
                'https://www.expertsphp.com/instagram-reels-downloader.php', data=p)
            html = r.content
            bsObj = BeautifulSoup(html, 'html.parser')
            with open('json/twitterBubble.json', 'r', encoding='utf8') as jfile:
                jdata1 = json.load(jfile)
            if 'mp4' in r.text:
                videos = bsObj.findAll(
                    'a', {'class': 'btn-sm'})
                for video in videos:
                    if 'mp4' in video['href']:
                        video_url = video['href']
                    else:
                        img_url = video['href']
                msg.append(VideoSendMessage(
                    original_content_url=video_url, preview_image_url=img_url))
            else:
                imgs = bsObj.findAll('img', {'alt': 'Thumbnail'})
                for img in imgs:
                    content = img['title']
                    img_url = img['src']
                jdata1['body']['contents'][0]['url'] = 'https://cdn.discordapp.com/attachments/856516846144192543/1102493248120963153/R-18_icon.svg.png'
                jdata1['body']['contents'][1]['text'] = '@' + \
                    get_message.split('/')[-3]
                jdata1['body']['contents'][2][
                    'text'] = '(Only the first image will be showed)'
                jdata1['body']['contents'][4]['contents'][0]['text'] = content
                jdata1['body']['contents'][4]['contents'][2]['contents'][1]['text'] = 'N/A'
                jdata1['body']['contents'][4]['contents'][3]['contents'][1]['text'] = 'N/A'
                msg.append(FlexSendMessage('tweet', jdata1))
                msg.append(ImageSendMessage(
                    original_content_url=img_url, preview_image_url=img_url))
    line_reply(msg, event)
    with open('twitterStack.txt', 'w') as f:
        f.write('')
    #------------------- below is for Twitter API, but it's not work anymore :( ---------------------------------------#
    # urlElement = get_message.split('/')
    # auth = tweepy.OAuthHandler(
    #     os.getenv('TWITTER_APP_KEY', None), os.getenv('TWITTER_APP_SECRET', None))
    # auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN', None), os.getenv(
    #     'TWITTER_ACCESS_TOKEN_SECRET', None))
    # api = tweepy.API(auth)
    # tweet = api.get_status(urlElement[-1])
    # with open('json/twitterBubble.json', 'r', encoding='utf8') as jfile:
    #     jdata1 = json.load(jfile)
    # ctn = []
    # jdata1['body']['contents'][0]['url'] = tweet.user.profile_image_url.replace(
    #     'http', 'https')
    # jdata1['body']['contents'][1]['text'] = tweet.user.name
    # jdata1['body']['contents'][2]['text'] = '@'+tweet.user.screen_name
    # jdata1['body']['contents'][3]['contents'][1]['text'] = str(
    #     tweet.user.followers_count)
    # jdata1['body']['contents'][5]['contents'][0]['text'] = tweet.text
    # jdata1['body']['contents'][5]['contents'][2]['contents'][1]['text'] = str(
    #     tweet.retweet_count)
    # jdata1['body']['contents'][5]['contents'][3]['contents'][1]['text'] = str(
    #     tweet.favorite_count)
    # tweet = api.get_status(urlElement[-1], tweet_mode="extended")
    # msg = []
    # msg.append(FlexSendMessage('tweet', jdata1))
    # try:
    #     url = tweet.extended_entities["media"][0]["video_info"]["variants"][0]["url"].split('?')[
    #         0]
    #     url2 = tweet.extended_entities["media"][0]['media_url']
    #     if('https' not in url2):
    #         url2 = url2.replace('http', 'https')
    #     msg.append(VideoSendMessage(
    #         original_content_url=url, preview_image_url=url2))
    # except:
    #     with open('json/imgBubble.json', 'r', encoding='utf8') as jfile:
    #         jdata2 = json.load(jfile)
    #     if 'media' in tweet.entities:
    #         img_url = ''
    #         for media in tweet.extended_entities['media']:
    #             tmp = copy.deepcopy(jdata2)
    #             if('https' not in media['media_url']):
    #                 tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url'].replace(
    #                     'http', 'https')
    #             else:
    #                 tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url']
    #             img_url = tmp['hero']['url']
    #             ctn.append(tmp)
    #         img_save(img_url, event)
    #     if len(ctn) > 1:
    #         with open('json/carousel.json', 'r', encoding='utf8') as jfile:
    #             jdata = json.load(jfile)
    #         jdata['contents'] = ctn
    #         reply = jdata
    #         msg.append(FlexSendMessage('tweet', reply))
    #     elif len(ctn) == 1:
    #         msg.append(ImageSendMessage(
    #             original_content_url=media['media_url'].replace('http', 'https'), preview_image_url=media['media_url'].replace('http', 'https')))
    # line_reply(msg, event)


def bahaLogin():
    rs = requests.session()
    data = {
        'uid': os.getenv('baha_UID', None),
        'passwd': os.getenv('baha_PW', None),
        'vcode': '7045'
    }
    rs.headers.update({
        'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
        'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
        'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
        'x-bahamut-app-version': '251',
        'content-type': 'application/x-www-form-urlencoded',
        'content-length': '44',
        'accept-encoding': 'gzip',
        'cookie': 'ckAPP_VCODE=7045'
    })
    request = rs.post(
        'https://api.gamer.com.tw/mobile_app/user/v3/do_login.php', data=data)
    rs.headers = {
        'user-agent': 'Bahadroid (https://www.gamer.com.tw/)',
        'x-bahamut-app-instanceid': 'cc2zQIfDpg4',
        'x-bahamut-app-android': 'tw.com.gamer.android.activecenter',
        'x-bahamut-app-version': '251',
        'accept-encoding': 'gzip',
    }
    return rs


def F_bahamutePreview(get_message, event):
    rs = bahaLogin()
    request = rs.get(get_message)
    html = request.text
    html = html.replace('</div>', '\n</div>')
    bsObj = BeautifulSoup(html, 'html.parser')
    article = ''
    title = bsObj.findAll('h1', {'class': 'title'})[0].text
    username = bsObj.findAll('a', {'class': 'username'})[0].text
    uid = bsObj.findAll('a', {'class': 'userid'})[0].text
    gp = bsObj.findAll('a', {'class': 'tippy-gpbp-list'})[0].text
    bp = bsObj.findAll('a', {'class': 'tippy-gpbp-list'})[1].text
    rawCtn = bsObj.findAll('div', {'class': 'c-article__content'})[0]
    # ctn = rawCtn.findAll('div')
    article += '\n'+title+'\n\n'+'-'*len(title)+'\n\n'
    article += f'樓主: {username} {uid}\n\n推(GP): {gp}\n噓(BP): {bp}' + \
        '\n\n'+'-'*len(title)+'\n\n'
    # last_url = []
    # last_ctn = ''
    # for row in ctn:
    #     if row.text != last_ctn:
    #         article += row.text
    #     last_ctn = row.text
    #     try:
    #         block = rawCtn.findAll('a', {'target': '_blank'})
    #         for url in block:
    #             if url not in last_url:
    #                 article += '\n'+url['href']+'\n'
    #             last_url.append(url)
    #     except:
    #         pass
    #     try:
    #         block = rawCtn.findAll('a', {'class': 'photoswipe-image'})
    #         for url in block:
    #             if url not in last_url:
    #                 article += '\n'+url['href']+'\n'
    #             last_url.append(url)
    #     except:
    #         pass
    #     try:
    #         url = row.find('iframe', {'class': 'lazyload'})['data-src']
    #         if url not in last_url:
    #             article += '\n'+url+'\n'
    #         last_url.append(url)
    #     except:
    #         pass
    # if len(article) > 5000:
    #     article = article[:5000]
    text_reply(article, event)


def F_bahamuteHomePreview(get_message, event):
    rs = bahaLogin()
    request = rs.get(get_message)
    html = request.text
    html = html.replace('</div>', '\n</div>')
    bsObj = BeautifulSoup(html, 'html.parser')
    article = ''
    ctitle = bsObj.findAll('h1', {'class': 'c-title'})[0].text.split(' ')
    date = f'{ctitle[0][2:]} {ctitle[1][:5]}'
    title = ctitle[1][5:]
    t = 2
    while t < len(ctitle):
        title += ' ' + ctitle[t]
        t += 1
    username = bsObj.findAll('p', {'class': 'gnn_man2'})[0].text[1:]
    rawCtn = bsObj.findAll('div', {'class': 'home_box'}
                           )[0]
    ctn = rawCtn.findAll('div')
    info = ctn[-1].text.split('\n')
    gp = info[1]
    collect = info[2]
    article += '\n'+f'{title}\n\n'+'------\n\n' + \
        f'{date}\n{username}\nGP: {gp}\n收藏: {collect}\n\n'
    # article += '\n'+f'{title}\n\n'+'-'*len(title)+'\n\n'
    # article += f'{date}\n{username}\nGP: {gp}\n收藏: {collect}\n\n' + \
    #     '-'*len(title)+'\n\n'
    last_url = []
    last_ctn = ''
    for row in ctn[:-1]:
        try:
            block = row.findAll('img', {'class': 'lazyload'})
            for url in block:
                if url not in last_url:
                    article += '\n'+url['data-src']+'\n'
                last_url.append(url)
        except:
            pass
        try:
            block = row.findAll('a', {'class': 'photoswipe-image'})
            for url in block:
                if url not in last_url:
                    article += '\n'+url['href']+'\n'
                last_url.append(url)
        except:
            pass
        try:
            url = row.find('iframe', {'class': 'lazyload'})['data-src']
            if url not in last_url:
                article += '\n'+url+'\n'
            last_url.append(url)
        except:
            pass
        if row.text != last_ctn:
            article += row.text
        last_ctn = row.text
    if len(article) > 5000:
        article = article[:5000]
    text_reply(article, event)


def F_randnum(get_message, event):
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
    text_reply(num, event)


def F_rate(get_message, send_headers, event):
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
    text_reply(words, event)



def F_faceDetect(event, id):
    img = cv2.imread(f"{id}.png")
    net = cv2.dnn.readNetFromCaffe(
        "deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")
    h, w = img.shape[:2]
    color = (0, 255, 0)
    blob = cv2.dnn.blobFromImage(cv2.resize(
        img, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < 0.5:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        # text = "{:.2f}%".format(confidence * 100)
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(img, (startX, startY), (endX, endY),
                      color, 2)
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faceRects = face_classifier.detectMultiScale(grayImg, scaleFactor=1.3)
    if len(faceRects):
        for faceRect in faceRects:
            x, y, w, h = faceRect
            cv2.rectangle(img, (x, y), (x + h, y + w), color, 2)
    cv2.imwrite("face.png", img)
    img_reply(uploadIMG("face.png"), event)


def F_removeBG(event, id):
    img = cv2.imread(f"{id}.png")
    segmentor = SelfiSegmentation()
    rBGimg = segmentor.removeBG(img, (255, 255, 255), threshold=0.99)
    cv2.imwrite("rBG.png", rBGimg)
    img_reply(uploadIMG("rBG.png"), event)


def F_manga(event, id):
    th1 = 70
    th2 = 120
    img = cv2.imread(f"{id}.png")
    img = cv2.GaussianBlur(img, (0, 0), 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edge = 255 - cv2.Canny(gray, 80, 120)
    gray[gray <= th1] = 0
    gray[gray >= th2] = 255
    img = cv2.bitwise_and(gray, edge)
    blur = cv2.GaussianBlur(img, (0, 0), 10)
    img = cv2.addWeighted(img, 1.5, blur, -0.5, 0)
    cv2.imwrite("MANGA.png", img)
    img_reply(uploadIMG("MANGA.png"), event)


def F_searchByIMG(id, x):
    sauce = SauceNao(os.getenv('SauceNao', None))
    results = sauce.from_url(uploadIMG(f"{id}.png"))
    reply = ''
    if x.isdigit():
        x = int(x)
        times = x if len(results) >= x else len(results)
        for i in range(times):
            if len(results[i].urls) > 0:
                reply += f'{results[i].title}\n{results[i].urls[0]}\n\n\n'
            else:
                reply += f'{results[i].title}\n\n\n'
    else:
        if len(results[0].urls) > 0:
            reply = f'{results[0].title}\n{results[0].urls[0]}'
        else:
            reply = results[0].title
    return reply


def F_vote(event):
    reply = json.load(open('json/vote.json', 'r', encoding='utf-8'))
    flex_reply('vote', reply, event)


def LLM(get_message, event, mode='text'):
    prompt = get_message[4:]
    translator = googletrans.Translator()
    Lang = translator.detect(prompt)
    prompt = translator.translate(prompt, dest='en').text
    palm.configure(api_key=os.getenv('PaLM_KEY', None))
    models = [m for m in palm.list_models(
    ) if 'generateText' in m.supported_generation_methods]
    model = models[0].name
    if mode == 'text':
        print(prompt)
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=1.0,
            # The maximum length of the response
            max_output_tokens=800,
        )
        words = completion.result
        if words == "no":
            words = random.choice(['yes', 'no'])
        if words == None:
            words = 'yes'
    elif mode == 'chat':
        sheet = sheet_reload("1jZs62-bWgOZDJXHZZBHw09xL2PmG9kP1eotrp6l7aRg")
        if prompt == 'r':
            memories = []
            sheet.clear()
            text_reply("已刪除所有記憶", event)
        else:
            data = sheet.get_all_values()
            memories = [data[i][0] for i in range(len(data))]
            memories.append(prompt)
            msgs = []
            for i in range(len(memories)):
                msgs.append({'author': f'{i%2}', 'content': memories[i]})
            response = palm.chat(messages="Hi")
            response.messages = msgs
            response = response.reply(prompt)
            words = response.last
            if words == None:
                words = "I don't know."
            memories.append(words)
            sheet.update(f'A{len(memories)-1}:A{len(memories)}',
                         [[prompt], [words]])
    reply = translator.translate(words, dest='zh-tw').text
    text_reply(reply, event)

