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
import tweepy
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
# from revChatGPT.ChatGPT import Chatbot

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


def audio_reply(URL, event):
    reply = AudioSendMessage(
        original_content_url=URL, duration=100000)
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


def bully(n, List, event):
    if n > 0:
        randNum = random.randint(1, n)
        if randNum == 1:
            text = random.choice(List)
            text_reply(text, event)


def F_bullyManager(split, event):
    sheet, bully_names, bully_p, bully_words = bully_reload()
    if len(split) == 2:
        if split[1] == 'list':
            keys = ""
            for i in range(len(bully_names)):
                if int(bully_p[i]) != 0:
                    keys += bully_names[i]+'\n'
            text_reply(f'名單:\n{keys}', event)
        elif split[1] in bully_names:
            p = bully_p[bully_names.index(split[1])]
            words = bully_words[bully_names.index(split[1])]
            text_reply(f'p:{p}\nwords:\n{words}', event)
        else:
            text_reply(f'名單無此人', event)
    elif split[2] == 'p':
        if split[1] in bully_names:
            bully_p[bully_names.index(split[1])] = split[3]
            sheet.update_cell(bully_names.index(
                split[1])+1, 2, split[3])
            text_reply(f'{split[1]}的被霸凌機率已調整為1/{split[3]}', event)
        else:
            sheet.append_row([split[1], split[3], f'{split[1]}去死'])
            text_reply(f'{split[1]}未登錄霸凌名單，現已登錄且將被霸凌機率設為1/{split[3]}', event)
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
                    f'資料庫已加入「{split[3]}」\n現已收錄:{bully_words[bully_names.index(split[1])]}', event)
            else:
                text_reply('此句已存在', event)
        else:
            sheet.append_row([split[1], '5', split[3]])
            text_reply(f'{split[1]}未登錄霸凌名單\n現已登錄且收錄:[\'{split[3]}\']', event)
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
                    f'資料庫已刪除「{split[3]}」\n現已收錄:{bully_words[bully_names.index(split[1])]}', event)
            else:
                text_reply('此句不存在', event)
        else:
            text_reply(f'{split[1]}未登錄霸凌名單', event)
    elif split[2] == 'del':
        if split[1] in bully_names:
            bully_p[bully_names.index(split[1])] = '0'
            sheet.update_cell(bully_names.index(
                split[1])+1, 2, '0')
            keys = ""
            for i in range(len(bully_names)):
                if int(bully_p[i]) != 0:
                    keys += bully_names[i]+'\n'
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
    if get_message.split()[1] in ['?', '？']:
        text_reply(gtts.lang.tts_langs(), event)
        return
    elif get_message.split()[1].lower() in list(gtts.lang.tts_langs().keys()):
        LAN = get_message.split()[1].lower()
        tts = gtts.gTTS(text=get_message[8:], lang=LAN)
        tts.save("tmp.m4a")
    else:
        LAN = 'zh-tw'
        tts = gtts.gTTS(text=get_message[5:], lang=LAN)
        tts.save("tmp.m4a")
    data = pyscord_storage.upload('tmp.m4a', 'tmp.m4a')['data']
    print(data['url'])
    audio_reply(data['url'], event)


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
        text_reply(text, event)
    else:
        index = int(split[1][1:])
        if index > len(URL):
            index = len(URL)
        text_reply(URL[index-1], event)


def F_nh(split, get_message, event):
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
    text_reply(content, event)


def F_ytPreview(l_get_message, jdata, event):
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
        text = title + '\n' +\
            '作者: '+author + '\n' +\
            '-'+'\n' +\
            content
    if len(text) > 5000:
        text = text[:5000]
    text_reply(text, event)


def F_twitterPreview(get_message, event):
    urlElement = get_message.split('/')
    auth = tweepy.OAuthHandler(
        os.getenv('TWITTER_APP_KEY', None), os.getenv('TWITTER_APP_SECRET', None))
    auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN', None), os.getenv(
        'TWITTER_ACCESS_TOKEN_SECRET', None))
    api = tweepy.API(auth)
    tweet = api.get_status(urlElement[-1])
    with open('json/twitterBubble.json', 'r', encoding='utf8') as jfile:
        jdata1 = json.load(jfile)
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
    tweet = api.get_status(urlElement[-1], tweet_mode="extended")
    msg = []
    msg.append(FlexSendMessage('tweet', jdata1))
    try:
        url = tweet.extended_entities["media"][0]["video_info"]["variants"][0]["url"].split('?')[
            0]
        url2 = tweet.extended_entities["media"][0]['media_url']
        if('https' not in url2):
            url2 = url2.replace('http', 'https')
        msg.append(VideoSendMessage(
            original_content_url=url, preview_image_url=url2))
    except:
        with open('json/imgBubble.json', 'r', encoding='utf8') as jfile:
            jdata2 = json.load(jfile)
        if 'media' in tweet.entities:
            img_url = ''
            for media in tweet.extended_entities['media']:
                tmp = copy.deepcopy(jdata2)
                if('https' not in media['media_url']):
                    tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url'].replace(
                        'http', 'https')
                else:
                    tmp['hero']['url'] = tmp['hero']['action']['uri'] = media['media_url']
                img_url = tmp['hero']['url']
                ctn.append(tmp)
            img_save(img_url, event)
        if len(ctn) > 1:
            with open('json/carousel.json', 'r', encoding='utf8') as jfile:
                jdata = json.load(jfile)
            jdata['contents'] = ctn
            reply = jdata
            msg.append(FlexSendMessage('tweet', reply))
        elif len(ctn) == 1:
            msg.append(ImageSendMessage(
                original_content_url=media['media_url'].replace('http', 'https'), preview_image_url=media['media_url'].replace('http', 'https')))
    line_reply(msg, event)


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
    ctn = rawCtn.findAll('div')
    article += '\n'+title+'\n\n'+'-'*len(title)+'\n\n'
    article += f'樓主: {username} {uid}\n\n推(GP): {gp}\n噓(BP): {bp}' + \
        '\n\n'+'-'*len(title)+'\n\n'
    last_url = []
    last_ctn = ''
    for row in ctn:
        if row.text != last_ctn:
            article += row.text
        last_ctn = row.text
        try:
            block = rawCtn.findAll('a', {'target': '_blank'})
            for url in block:
                if url not in last_url:
                    article += '\n'+url['href']+'\n'
                last_url.append(url)
        except:
            pass
        try:
            block = rawCtn.findAll('a', {'class': 'photoswipe-image'})
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
    if len(article) > 5000:
        article = article[:5000]
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
    article += '\n'+f'{title}\n\n'+'-'*len(title)+'\n\n'
    article += f'{date}\n{username}\nGP: {gp}\n收藏: {collect}\n\n' + \
        '-'*len(title)+'\n\n'
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


# def F_chatGPT(get_message, event):
#     OPENAI_EMAIL = os.getenv("OPENAI_EMAIL")
#     OPENAI_PASSWORD = os.getenv("OPENAI_PASSWORD")
#     chat = ChatClient(OPENAI_EMAIL, OPENAI_PASSWORD)
#     answer = chat.interact(get_message[5:])
#     text_reply(answer, event)
#     with open("json/chatGPT_config.json", encoding="utf-8") as f:
#         config = json.load(f)
#     chatbot = Chatbot(config, debug=False)
#     prompt = "\nYou:\n"+get_message[5:]
#     message = chatbot.get_chat_response(prompt)
#     text_reply(message["message"], event)


# def F_objectDetect(event):
#     execution_path = os.getcwd()
#     detector = ObjectDetection()
#     detector.setModelTypeAsTinyYOLOv3()
#     detector.setModelPath(os.path.join(execution_path, "yolo-tiny.h5"))
#     detector.loadModel()
#     detector.detectObjectsFromImage(input_image=os.path.join(execution_path, "IMG.png"), output_image_path=os.path.join(
#         execution_path, "object.png"), minimum_percentage_probability=30,  extract_detected_objects=True)
#     img_reply(uploadIMG("object.png"), event)


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


def F_teacherReplace(event, id):
    img = cv2.imread(f"{id}.png")
    net = cv2.dnn.readNetFromCaffe(
        "deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")
    h, w = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(
        img, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        img2 = cv2.imread("teacher.jpg")
        confidence = detections[0, 0, i, 2]
        if confidence < 0.5:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        print(startX, startY, endX, endY)
        img2 = cv2.resize(img2, (endX-startX, endY-startY),
                          interpolation=cv2.INTER_AREA)
        img[startY:endY, startX:endX] = img2
    cv2.imwrite("teacherface.png", img)
    img_reply(uploadIMG("teacherface.png"), event)


def F_oppaiDetect(event, id):
    img = cv2.imread(f"{id}.png")
    color = (0, 255, 0)
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    oppai_classifier = cv2.CascadeClassifier('./xml/cascade_oppai.xml')
    oppaiRects = oppai_classifier.detectMultiScale(grayImg, scaleFactor=1.3)
    if len(oppaiRects):
        for oppaiRect in oppaiRects:
            x, y, w, h = oppaiRect
            cv2.rectangle(img, (x, y), (x + h, y + w), color, 2)
    cv2.imwrite("oppai.png", img)
    img_reply(uploadIMG("oppai.png"), event)


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

# def F_bot():
    # line_bot_api.reply_message(  # 回復傳入的訊息文字
    #         event.reply_token,
    #         TemplateSendMessage(
    #             alt_text='Buttons template',
    #             template=ButtonsTemplate(
    #                 title='遊戲選單',
    #                 text='請選擇遊戲',
    #                 actions=[
    #                     MessageTemplateAction(
    #                         label='game1',
    #                         text='game1',
    #                         data='A&game1'
    #                     ),
    #                     MessageTemplateAction(
    #                         label='game2',
    #                         text='game2',
    #                         data='A&game2'
    #                     ),
    #                     MessageTemplateAction(
    #                         label='game3',
    #                         text='Upcoming...',
    #                         data='A&game3'
    #                     )
    #                 ]
    #             )
    #         )
    #     )
